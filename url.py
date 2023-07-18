from flask import Flask, flash, render_template, request, redirect, url_for, session
from bs4 import BeautifulSoup
import requests
import operator
import validators
import re
from baglac import isStopWord
import string

app = Flask(__name__)


wordcount = {}
wordcount2 = {}
app.secret_key = "hello"


@app.route("/")
def index():
    return render_template("index.html")

# Create WordCounts


def createWordCount(text):

    wordcount = {}

    r = requests.get(text)
    source = BeautifulSoup(r.content, 'html.parser')

    for word in source.get_text().split():
        word = word.lower()
        punc = '''!()-[]{};:'", <>./?@#$%^&*_~'''
        for i in punc:
            word = word.strip(i)
        for i in punc:
            word = word.strip(i)
        if word not in wordcount:

            a = re.findall(r'\d+', word)
            if a == [] and word != "" and len(word) != 1:

                wordcount[word] = 1
            else:
                pass

        else:
            wordcount[word] += 1

    return wordcount


def createWordCountTitle(text):
    wordcount = {}

    r = requests.get(text)
    source = BeautifulSoup(r.content, 'html.parser')

    for word in source.title.string.split():
        word = word.lower()
        punc = '''!()-[]{};:'", <>./?@#$%^&*_~'''
        for i in punc:
            word = word.strip(i)
        for i in punc:
            word = word.strip(i)
        if word not in wordcount:

            a = re.findall(r'\d+', word)
            if a == [] and word != "" and len(word) != 1:

                wordcount[word] = 1
            else:
                pass

        else:
            wordcount[word] += 1

    return wordcount


def benzerlikYuzdeTitle(title, title2):
    toplamOrtak = 0
    toplamToplam = 0
    for i in title.keys():
        for j in title2.keys():
            if i == j:
                toplamOrtak += title[i]
                toplamOrtak += title2[j]
    for i in title.keys():
        toplamToplam += title[i]
    for j in title2.keys():
        toplamToplam += title2[j]

    benzerlikYuzde = (toplamOrtak/toplamToplam)*100
    #benzerlikYuzde = round(benzerlikYuzde, 2)

    return benzerlikYuzde


# Keys Detected


def keySearch(wordcount2):
    key = {}
    a = 0
    for i in range(0, 50):
        kontrol = isStopWord(
            max(wordcount2.items(), key=operator.itemgetter(1))[0])
        if kontrol:
            wordcount2.pop(
                max(wordcount2.items(), key=operator.itemgetter(1))[0])
        else:
            a += 1
            key[max(wordcount2.items(), key=operator.itemgetter(1))[
                0]] = wordcount2[max(wordcount2.items(), key=operator.itemgetter(1))[0]]
            wordcount2.pop(
                max(wordcount2.items(), key=operator.itemgetter(1))[0])
        if a == 5:
            break
    return key


# Benzerlik Orani


def similarityPercentage(anahtar, anahtar2):
    toplamOrtak = 0
    toplamToplam = 0
    for i in anahtar.keys():
        for j in anahtar2.keys():
            if i == j:
                toplamOrtak += anahtar[i]
                toplamOrtak += anahtar2[j]
    for i in anahtar.keys():
        toplamToplam += anahtar[i]
    for j in anahtar2.keys():
        toplamToplam += anahtar2[j]

    benzerlikYuzde = (toplamOrtak/toplamToplam)*100
    #benzerlikYuzde = round(benzerlikYuzde, 2)

    return benzerlikYuzde


def urlControl(wordcount):
    for i in wordcount:
        urlcontrol = validators.url(i)
        if urlControl == True:
            return i
    return


@app.route("/asama1", methods=["GET", "POST"])
def asama1():
    session["kontrol"] = False
    wordcount = {}
    if request.method == "POST":
        wordcount.clear()
        text = request.form['url']

        validUrl = validators.url(text)

        if validUrl:

            session["kontrol"] = True

            wordcount = createWordCount(text)

            #sayac = str(len(wordcount))

            flash("Indexleme islemi basarili bir sekilde gerceklesmistir!!", "success")

            return render_template("asama1.html", wordcount=wordcount)
            # return wordcount
        else:
            flash("Lutfen dogru bir url giriniz", "danger")
            return render_template("asama1.html")
    else:
        wordcount.clear()
        return render_template("asama1.html")


@app.route("/asama2", methods=["GET", "POST"])
def asama2():
    wordcount = {}
    wordcount2 = {}
    session["kontroll"] = False
    if request.method == "POST":
        wordcount.clear()
        wordcount2.clear()

        text = request.form['search']
        text2 = request.form['searchh']

        validUrl = validators.url(text)
        validUrl2 = validators.url(text2)

        if validUrl and validUrl2:

            session["kontroll"] = True

            wordcount = createWordCount(text)
            wordcount2 = createWordCount(text2)
            titleWordCount = createWordCountTitle(text)
            titleWordCount2 = createWordCountTitle(text2)

            flash("Indexleme islemi basarili bir sekilde gerceklesmistir!!", "success")

            anahtar = {}
            anahtar2 = {}

            anahtar = keySearch(wordcount)
            anahtar2 = keySearch(wordcount2)

            benzerlikyuzdeTitle = benzerlikYuzdeTitle(
                titleWordCount, titleWordCount2)
            benzerlikYuzde = similarityPercentage(anahtar, anahtar2)

            genelOran = ((benzerlikYuzde * 60) +
                         (benzerlikyuzdeTitle * 40))/100
            genelOran = round(genelOran, 2)
            return render_template("asama2.html", anahtar=anahtar, anahtar2=anahtar2, benzerlikYuzde=genelOran)

        else:
            flash("Lutfen dogru bir url giriniz", "danger")
            return render_template("asama2.html")
    else:
        wordcount.clear()
        return render_template("asama2.html")


@app.route("/asama3bilgi", methods=["GET", "POST"])
def asama3bilgi():

    if request.method == "POST":
        value = request.form['input']
        return redirect(url_for('asama3', value=value))

    else:
        return render_template("asama3bilgi.html")


def childKontrol(anaUrl, link):
    sayacLink = 0
    sayacUrl = 0
    link = link.strip("/")
    for i in link.split("/"):
        sayacLink += 1
    anaUrl = anaUrl.strip("/")
    for j in anaUrl.split("/"):
        sayacUrl += 1
    if (sayacLink - sayacUrl) == 1:
        return True
    else:
        return False


def urlListele(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.content, "html.parser")
    linkler = soup.find_all("a")
    liste = list()

    try:
        cikis = 0
        for link in linkler:

            if str(link.get("href")).find(url) == 0 and childKontrol(url, link.get("href")):
                if str(link.get("href")) not in liste:
                    liste.append(link.get("href"))

                    cikis += 1
                    if cikis > 2:
                        break

    except:
        pass

    return liste


def mainBenzerlikOran(anaUrl, subUrl):
    anaWordCount = {}
    anaAnahtar = {}
    anaTitleWordCount = {}

    subWordCount = {}
    subAnahtar = {}
    subTitleWordCount = {}

    anaWordCount = createWordCount(anaUrl)
    anaTitleWordCount = createWordCountTitle(anaUrl)
    anaAnahtar = keySearch(anaWordCount)

    subWordCount = createWordCount(subUrl)
    subTitleWordCount = createWordCountTitle(subUrl)
    subAnahtar = keySearch(subWordCount)

    benzerlikyuzdeTitle = benzerlikYuzdeTitle(
        anaTitleWordCount, subTitleWordCount)
    benzerlikYuzde = similarityPercentage(
        anaAnahtar, subAnahtar)

    oran = ((benzerlikYuzde * 50) +
            (benzerlikyuzdeTitle * 50))/100
    oran = round(oran, 2)

    return oran


def anahtarDondurma(url):
    WordCount = {}
    Anahtar = {}

    WordCount = createWordCount(url)
    Anahtar = keySearch(WordCount)

    return Anahtar


def esBul(kelime):
    url = "https://es-anlamli.gen.sx/?s=" + kelime
    r = requests.get(url)
    soup = BeautifulSoup(r.content, "html.parser")
    kelimeler = list()
    string = ""
    for k in soup.findAll('span', {'style': 'background: rgba(180,176,157,.15) none repeat scroll 0% 0%; -moz-background-clip: -moz-initial; -moz-background-origin: -moz-initial; -moz-background-inline-policy: -moz-initial; margin-left: 50px; color: blue; font-weight: bold;'}):
        string = k.text

    if(string == kelime):
        for k in soup.findAll('span', {'style': 'vertical-align:middle'}):
            string = k.text
            for i in string.split(","):
                kelimeler.append(i.strip(" "))

    return kelimeler


def esKelimeArama(kelimeSozlugu, kelime):

    for i in kelimeSozlugu.keys():
        if i == kelime:
            return True
    return False


def esKelimeKumesi(urlListesi):
    anaUrlEsKelime = []
    sayac = 0
    for i in urlListesi:
        kelimeSozlugu = createWordCount(i[1])
        anaUrlEsKelime.append([])
        for j in i[2].keys():
            esKelimeListesi = esBul(j)
            print(j)
            print(esKelimeListesi)
            for a in esKelimeListesi:

                if esKelimeArama(kelimeSozlugu, a):
                    anaUrlEsKelime[sayac].append(a)

        sayac += 1
    return anaUrlEsKelime


@app.route("/asama3", methods=["GET", "POST"])
def asama3():
    session["kontrol"] = False

    value = int(request.args['value'])

    if request.method == "POST":

        text = request.form['asama3Search']
        validUrl = validators.url(text)

        if validUrl:

            urlListe2 = []

            anaUrlYolla = []

            urlListeKatman2 = []
            urlListeKatman3 = []
            genelOranListesi = []
            for i in range(0, value):
                urlListe = []
                genelOran = 0

                urlListe += urlListele(request.form['asama'+str(i)])

                genelOran += mainBenzerlikOran(text,
                                               request.form['asama'+str(i)])

                urlListeKopya = []

                for j in urlListe:

                    altOran = mainBenzerlikOran(text, j)

                    urlListeKopya.append(j)
                    urlListeKatman2.append([altOran, j, anahtarDondurma(j)])

                for j in urlListeKopya:

                    urlListe += urlListele(j)
                    urlListe2 += urlListele(j)
                    for k in urlListele(j):
                        altOran = mainBenzerlikOran(text, k)
                        urlListeKatman3.append(
                            [altOran, k, anahtarDondurma(k)])

                print(urlListe)

                for s in urlListe:
                    oran = mainBenzerlikOran(text, s)
                    genelOran = round((genelOran + oran)/2, 2)

                genelOranListesi.append(genelOran)
                anaUrlYolla.append([mainBenzerlikOran(text, request.form['asama'+str(i)]),
                                    request.form['asama'+str(i)], anahtarDondurma(request.form['asama'+str(i)]), genelOran])
                print(genelOran)

            # Urlleri benzerlik oranlarına göre siraladik
            anaUrlYolla.sort(reverse=True)
            urlListeKatman2.sort(reverse=True)
            urlListeKatman3.sort(reverse=True)

            donguSayac = len(esKelimeKumesi(anaUrlYolla))
            anaSayfa = esKelimeKumesi(anaUrlYolla)

            for i in range(0, donguSayac):
                anaUrlYolla[i].append(anaSayfa[i])

            donguSayac = len(esKelimeKumesi(urlListeKatman2))
            anaSayfa = esKelimeKumesi(urlListeKatman2)

            for i in range(0, donguSayac):
                urlListeKatman2[i].append(anaSayfa[i])

            donguSayac = len(esKelimeKumesi(urlListeKatman3))
            anaSayfa = esKelimeKumesi(urlListeKatman3)

            for i in range(0, donguSayac):
                urlListeKatman3[i].append(anaSayfa[i])

            return render_template("asama3.html", value=value, anaUrlYolla=anaUrlYolla, urlListeKopya=urlListeKatman2, urlListe2=urlListeKatman3, genelOranListesi=genelOranListesi)
    else:
        wordcount.clear()
        return render_template("asama3.html", value=value)


# Bu modul terminalden calistirldiysa kosul icine giriliyor
if __name__ == "__main__":
    app.run(debug=True)
