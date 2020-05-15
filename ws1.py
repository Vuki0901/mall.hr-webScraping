import requests
from bs4 import BeautifulSoup
import bs4
import json

#prebacivanje cijene iz stringa u float (zarez u tocku, brisanje tocke iz broja)
def priceConvert(price):
    if '.' not in price and ',' in price:
        return float(price.split(' ')[0].replace(',','.'))

    elif '.' in price and ',' in price:
        string = price.split(' ')[0].replace(',','.')
        string = string.split('.')
        kune = string[:-1]; lipe = string[-1]
        cijena = "".join(br for br in kune)
        cijena += '.'+lipe
        return float(cijena)

    elif '.' in price and ',' not in price:
        price = price.split(' ')[0].split('.')
        return float("".join(price))

    elif '.' not in price and ',' not in price:
        return float(price.split(' ')[0])


def sortiranjeCijena(obj, n):
    #listaCijena => pomocna lista pomocu koje se usporeduju cijene svih proizvoda
    #listaProizvoda => lista u koju se spremaju svi sortirani prozivodi
    listaCijena = [10**100]*n; listaProizvoda = [0] * n; retObj = {}
    imena = list(obj.keys())

    for ime in imena:
        cijenaProizvoda = obj[ime]['trenutnaCijena']
        for i in range(len(listaCijena)):
            if cijenaProizvoda < listaCijena[i]:
                listaCijena.insert(i, cijenaProizvoda)
                listaProizvoda.insert(i, (ime, obj[ime]))
                break

    listaProizvoda = listaProizvoda[:n]
    for el in listaProizvoda:
        a = {el[0]: el[1]}
        retObj.update(a)
    return retObj

def sortiranjePopusta(obj, n):
    imena = list(obj.keys())
    listaPopusta = [-1]*n; listaProizvoda = [0]*n; retObj = {}

    for ime in imena:
        popust = float(obj[ime]['popust'][:-1])
        for i in range(len(listaPopusta)):
            if popust > listaPopusta[i]:
                listaPopusta.insert(i, popust)
                listaProizvoda.insert(i, (ime, obj[ime]))
                break
    listaProizvoda = listaProizvoda[:n]
    for el in listaProizvoda:
        a = {el[0]: el[1]}
        retObj.update(a)
    return retObj
def pretragaSvihProizvoda(upit):
    print(f'Pretrazujem proizvode {upit} ...')

    URL = 'https://www.mall.hr'
    QUERY = upit

    #sastavljanje linka
    queryUrl = '/trazenje?s='
    query = QUERY.split(' ')
    for word in query:
        queryUrl += word+'%20'
    url = URL+queryUrl[:-3]

    result = requests.get(url)
    soup = BeautifulSoup(result.content, 'html.parser')

    #svi div elementi sa prozivodima
    roba = soup.find_all('div', 'lst-product-item-body')

    proizvodi = {} #json
    for r in roba:
        obj = {}    #json
        for rr in r.contents:
            link = rr.find("a")
            if type(link) == bs4.element.Tag:
                break

        # sadasnja cijena
        cijena = r.find('span', class_='lst-product-item-price-value')
        pr = cijena.text.split()
        pr = priceConvert(pr[0] + ' ' + pr[1])

        # trazenje stare cijene
        try:
            #ako je cijena proizvoda snizena

            # del tag na stranici postoji samo ako je
            # proizvod snizen i ako ne postoji izbacio bi se error
            # te se radnja prebacuje na except blok naredbi
            staraCijena = r.find('del', class_='lst-product-item-price--retail')
            old = staraCijena.text.split()
            old = priceConvert(old[0] + ' ' + old[1])

            disc = '%.2f%%' % (100 - (pr / old * 100))

        except:
            # ako cijena proizvoda nije snizena
            old = pr
            disc = '0%'

        obj = {
            link.text: {
                'link': 'https://www.mall.hr' + link.attrs['href'],
                'trenutnaCijena': pr,
                'staraCijena': old,
                'popust': disc
            }
        }
        proizvodi.update(obj)

    print(f'Pronađeno {len(list(proizvodi.keys()))} proizvoda!')
    print('Pretraga zavrsena!')
    return proizvodi


def najboljePonude(obj, odabir):
    if odabir == '1':
        najjeftinijiProizvodi = sortiranjeCijena(obj, int(input('Koliko najjeftinijih proizvoda: '))) #n najjeftinijih proizvoda iz upita
        print(json.dumps(najjeftinijiProizvodi, indent=4, sort_keys=True))
    elif odabir == '2':
        najveciPopusti = sortiranjePopusta(obj, int(input('Koliko najvećih popusta: ')))
        print(json.dumps(najveciPopusti, indent=4, sort_keys=True))
    else:
        print(f'Opcija {odabir} ne postoji!')
        najboljePonude(pretragaSvihProizvoda(input('Unesi upit: ')), input('Najjeftiniji proizvodi(1) ili najveći popusti(2): '))


najboljePonude(pretragaSvihProizvoda(input('Unesi upit: ')), input('Najjeftiniji proizvodi(1) ili najveći popusti(2): '))