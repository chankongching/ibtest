products = ['AUD.CAD', 'AUD.CHF', 'AUD.CNH', 'AUD.HKD', 'AUD.JPY', 'AUD.NZD', 'AUD.SGD', 'AUD.USD', 'AUD.ZAR',
            'CAD.CHF', 'CAD.CNH', 'CAD.JPY', 'CHF.CNH', 'CHF.CZK', 'CHF.DKK', 'CHF.HUF', 'CHF.JPY', 'CHF.NOK',
            'CHF.PLN', 'CHF.SEK', 'CHF.TRY', 'CHF.ZAR', 'CNH.HKD', 'CNH.JPY', 'DKK.JPY', 'DKK.NOK', 'DKK.SEK',
            'EUR.AUD', 'EUR.CAD', 'EUR.CHF', 'EUR.CNH', 'EUR.CZK', 'EUR.DKK', 'EUR.GBP', 'EUR.HKD', 'EUR.HUF',
            'EUR.ILS', 'EUR.JPY', 'EUR.MXN', 'EUR.NOK', 'EUR.NZD', 'EUR.PLN', 'EUR.RUB', 'EUR.SEK', 'EUR.SGD',
            'EUR.TRY', 'EUR.USD', 'EUR.ZAR', 'GBP.AUD', 'GBP.CAD', 'GBP.CHF', 'GBP.CNH', 'GBP.CZK', 'GBP.DKK',
            'GBP.HKD', 'GBP.HUF', 'GBP.JPY', 'GBP.MXN', 'GBP.NOK', 'GBP.NZD', 'GBP.PLN', 'GBP.SEK', 'GBP.SGD',
            'GBP.TRY', 'GBP.USD', 'GBP.ZAR', 'HKD.JPY', 'KRW.AUD', 'KRW.CAD', 'KRW.CHF', 'KRW.EUR', 'KRW.GBP',
            'KRW.HKD', 'KRW.JPY', 'KRW.USD', 'MXN.JPY', 'NOK.JPY', 'NOK.SEK', 'NZD.CAD', 'NZD.CHF', 'NZD.JPY',
            'NZD.USD', 'SEK.JPY', 'SGD.CNH', 'SGD.JPY', 'TRY.JPY', 'USD.CAD', 'USD.CHF', 'USD.CNH', 'USD.CZK',
            'USD.DKK', 'USD.HKD', 'USD.HUF', 'USD.ILS', 'USD.JPY', 'USD.KRW', 'USD.MXN', 'USD.NOK', 'USD.PLN',
            'USD.RUB', 'USD.SEK', 'USD.SGD', 'USD.TRY', 'USD.ZAR', 'ZAR.JPY']

# print(products)

# for (var i = 0; i < products.length; i++) {
#    console.log(colors[i]);
#}

new_products = []

i = 0
while i < len(products):
    print(products[i])
    a,b = products[i].split('.')
    #print("a = " + a)
    #print("b = " + b)
    #     print(products[i])
    new_products.append(b + '.' + a)
    i += 1

# print(new_products)
