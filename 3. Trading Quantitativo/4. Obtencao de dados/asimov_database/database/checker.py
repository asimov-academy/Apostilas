import numpy as np
import pandas as pd
import asimov_simulator as ad
from asimov_simulator.modules.utils import *

class Checker:
    def __init__(self, blueprint):
        self.md = ad.MarketData(blueprint=blueprint)
        self.symbols = blueprint.get('symbols')

    def _non_increasing(self,L):
        return all(x>=y for x, y in zip(L, L[1:]))

    def _non_decreasing(self,L):
        return all(x<=y for x, y in zip(L, L[1:]))

    def _is_zero(self,L):
        return all(v == 0 for v in L)

    def tests(self):
        check = 0
        j=0

        for i in range(self.md.data_store.length):
            self.md.data_store.next()
            j+=1
            if self.md.last_message[NOTIFY] == True:
                # Checa spread igual ou menor que 0 
                for symb in self.symbols:
                    if (self.md.book[symb][1][0, 0] - self.md.book[symb][0][0, 0] <= 0) and (self.md.book[symb][1][0, 0] != 0):
                        print('[ MARKET DATA ] Spread menor ou igual a 0 - Error in {}. i: {}'.format(symb, i))
                        check = 1
                        break
                    # A cada 1000 iterações checa se os valores são monotônicos(crescente -ASK e decrescente -BID )    
                    if (j%1000 == 0):    
                        first_0_bid = (np.where(self.md.book[symb][0][:, 0] == 0))[0]
                        first_0_ask = (np.where(self.md.book[symb][1][:, 0] == 0))[0]
                        if (len(first_0_bid) != 0) and (len(first_0_ask) != 0):
                            if (not self._non_increasing(self.md.book[symb][0][:, 0][:first_0_bid[0]-1])) or (not self._non_decreasing(self.md.book[symb][1][:, 0][:first_0_ask[0]-1])):
                                print('[ MARKET DATA ] Error de consistência de preço - Error in {}. i: {}'.format(symb, i))
                                check = 1
                                break
                            # A cada 1000 iterações checa se após o primeiro 0 todos os valores são 0   
                            if (not self._is_zero(self.md.book[symb][0][:, 0][first_0_bid[0]:])) or (not self._is_zero(self.md.book[symb][1][:, 0][first_0_ask[0]:])):
                                print('[ MARKET DATA ] Valor diferente de 0 depois do termino dos níveis - Error in {}. i: {}'.format(symb, i))
                                check = 1
                                break
         
            if check == 1:
                break

        if check == 0:
            print('[ MARKET DATA ] Teste 1, 2 e 3 - OK')
    


if __name__ == '__main__':

    from asimov_database import Checker


    blueprint = {'symbols' : ['DOLH20',
                            'WDOH20'],
                'date' : '2020-01-31',
                'local_sim' : False,
                'dont_start' : False,
                'log' : False,
                'log_period' : 500}


    test = Checker(blueprint)

    test.tests()