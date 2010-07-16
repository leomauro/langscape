import random
from langscape.ls_const import*
from langscape.trail.nfatracer import TokenTracer
from langscape.sourcetools.tokgen import TokenGenerator

class SourceGen(object):
    '''
    A source generator shall create random expressions based on a set of existing
    phrases.

    - expressions, derived from a given
    - phrases, derived from a subphrase
    - phrases, fixed at some points
    - random assemblages of existing phrases
    - try each possible branch
    - minimal random mutation
    '''
    def __init__(self, langlet, kind = "parse"):
        self.langlet   = langlet
        self.tokgen = TokenGenerator(langlet)

    def get_right_par(self, nid):
        raise NotImplementedError

    def get_left_par(self, nid):
        raise NotImplementedError

    def gen_token_string(self, nid):
        '''
        This method is langlet specific. It may be overwritten in subclasses.
        '''
        raise NotImplementedError


class GPSourceGen(SourceGen):
    def __init__(self, *args, **kwd):
        super(GPSourceGen, self).__init__(*args, **kwd)
        self.population = []  # sequence of (individual, fitness-value) tuples

    def display_results(self):
        pass

    def fitness(self, individual):
        raise NotImplementedError

    def init_population(self):
        raise NotImplementedError

    def terminate(self):
        raise NotImplementedError

    def mutate(self, individual):
        raise NotImplementedError

    def evolve(self, size = 100, generations = 100):
        self.init_population(size)
        g = 0
        k = size/2
        while g<generations:
            print "GENERATION", g+1
            if self.terminate():
                self.display_results()
                return
            new_population = []
            for individual, fit in self.population:
                if fit==-1:
                    fit_val = self.fitness(individual)
                    new_population.append((individual, fit_val))
                else:
                    new_population.append((individual, fit))
            new_population.sort(key = lambda x: - x[1])
            for i, (individual, fit) in enumerate(new_population[:k]):
                while True:
                    mutated = self.mutate(individual)
                    if mutated:
                        break
                new_population[k+i] = (mutated, -1)
            self.population = new_population
            g+=1
        self.terminate()
        self.display_results()


    def _seek_random_item(self, gene, trials):
         n = len(gene) - 1
         if len(trials) == n:
             trials.clear()
         while True:
             k = random.randrange(-1, n)
             if k not in trials:
                 break
         trials.add(k)
         tracer = TokenTracer(self.langlet)
         selection = []
         for i, tok in enumerate(gene):
             if i<=k:
                 tracer.select(tok[0])
             else:
                 break
         selection = list(tracer.selectables())
         m = random.randrange(0, len(selection))
         T = selection[m]
         return k, T, tracer

    def _check_gene(self, gene):
        tr = TokenTracer(self.langlet)
        try:
            res, idx = tr.check(gene)
        except (KeyError, TypeError):
            print gene
            raise
        return res


    def insert(self, g):
        trials = set()
        while True:
            gene = g[:]
            n = len(gene) - 1
            k, T, tracer = self._seek_random_item(gene, trials)
            if T is None:
                continue
            value = self.gen_token_string(T+SYMBOL_OFFSET)
            gene.insert(k+1, [T, value])
            n+=1
            R = self.get_right_par(T+SYMBOL_OFFSET)  # TODO: consider 'extended braces'
            if R:
                R-=SYMBOL_OFFSET
                i = 1
                loc = []
                while k+i<n:
                    try:
                        selection = tracer.select(gene[k+i][0])
                    except NonSelectableError:
                        break
                    if R in selection:
                        loc.append(k+i)
                    i+=1
                if loc:
                    value = self.gen_token_string(R+SYMBOL_OFFSET)
                    while loc:
                        m = loc[random.randrange(0, len(loc))]
                        gene.insert(m+1, [R, value])
                        tr = TokenTracer(self.langlet)
                        res, idx = tr.check(gene)
                        if res == True:
                            return gene
                        else:
                            loc.remove(m)
                    continue
                else:
                    continue
            else:
                if self._check_gene(gene):
                    return gene
                else:
                    continue


    def delete(self, g):
        visited = set()
        while True:
            n = len(g) - 1
            if len(visited)>=n:
                return g
            gene = g[:]
            k = random.randrange(0, n)
            visited.add(k)
            T = gene[k+1][0]
            del gene[k+1]
            n-=1
            R = self.get_right_par(T+SYMBOL_OFFSET)  # TODO: consider 'extended braces'
            loc = []
            if R:
                R-=SYMBOL_OFFSET
                for i, tok in enumerate(gene[k+1:]):
                    if tok[0] == R:
                        loc.append(i+k+1)
            else:
                L = self.get_left_par(T+SYMBOL_OFFSET)
                if L:
                    L-=SYMBOL_OFFSET
                    for i, tok in enumerate(gene[:k]):
                        if tok[0] == L:
                            loc.append(i)
            if loc:
                while loc:
                    m = loc[random.randrange(0, len(loc))]
                    backup = gene[m]
                    del gene[m]
                    tr = TokenTracer(self.langlet)
                    res, idx = tr.check(gene)
                    if res == True:
                        return gene
                    else:
                        loc.remove(m)
                        gene.insert(m, backup)
                continue
            else:
                if self._check_gene(gene):
                    return gene
                else:
                    continue

    def subst(self, g):
        trials = set()
        n = len(g) - 1
        while True:
            gene = g[:]
            k = random.randrange(-1, n)
            tracer = TokenTracer(self.langlet)
            for i, tok in enumerate(gene):
                if i<=k:
                    tracer.select(tok[0])
                else:
                    break
            selection = list(tracer.selectables())
            while k+1<n:
                if len(selection) == 1:
                    k+=1
                    selection = list(tracer.select(gene[k][0]))
                    continue
                while selection:
                    m = random.randrange(0, len(selection))
                    T = selection[m]
                    selection.remove(T)
                    if T is None:
                        continue
                    value = self.gen_token_string(T+SYMBOL_OFFSET)
                    backup = gene[k+1]
                    if backup[1] == value:
                        continue
                    gene[k+1] = [T, value]
                    tr = TokenTracer(self.langlet)
                    try:
                        res, idx = tr.check(gene)
                    except (KeyError, TypeError):
                        print gene
                        raise
                    if res == True:
                        return gene
                    else:
                        gene[k+1] = backup
                k+=1

