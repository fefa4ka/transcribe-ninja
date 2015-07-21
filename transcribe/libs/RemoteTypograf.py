# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
    remotetypograf.py
    python-implementation of ArtLebedevStudio.RemoteTypograf class (web-service client)
    
    Copyright (c) Art. Lebedev Studio | http://www.artlebedev.ru/

    Typograf homepage: http://typograf.artlebedev.ru/
    Web-service address: http://typograf.artlebedev.ru/webservices/typograf.asmx
    WSDL-description: http://typograf.artlebedev.ru/webservices/typograf.asmx?WSDL
    
    Default charset: UTF-8

    Python version 
    Author: Sergey Lavrinenko (s.lavrinenko@gmail.com)
    Version: 1.0 (2007-05-18) based on script by Andrew Shitov (ash@design.ru)

    Example:
        from RemoteTypograf import RemoteTypograf
            rt = RemoteTypograf()
        # rt = RemoteTypograf('windows-1251')
        print rt.processText ('"Âû âñå åùå êîå-êàê âåðñòàåòå â "Âîðäå"? - Òîãäà ìû èäåì ê âàì!"');
"""


import socket

class RemoteTypograf:

    _entityType = 4
    _useBr = 1
    _useP = 1
    _maxNobr = 3
    _encoding = 'UTF-8'

    def __init__(self, encoding='UTF-8'):
        self._encoding = encoding


    def htmlEntities(self):
        self._entityType = 1


    def xmlEntities(self):
        self._entityType = 2


    def mixedEntities(self):
        self._entityType = 4


    def noEntities(self):
        self._entityType = 3


    def br(self, value):
        if value:
            self._useBr = 1
        else:
            self._useBr = 0

    
    def p(self, value):
        if value:
            self._useP = 1
        else:
            self._useP = 0

    
    def nobr(self, value):
        if value:
            self._maxNobr = value
        else:
            self._maxNobr = 0

    def prettyText(self, text):
        # Если запятая в конце, то прибавляем следующий кусок
        # Ставим точку, если ничего не стоит
        text = text.strip()

        if text[-1] not in [',', '.', '!', '?']:
            text += '.'

        # если запятая. ставим точку
        if text[-1] == ",":
            text = text[0:len(text) - 1] + "."

        # Каждое предложение начинается с большой буквы
        # После . , ! ? ... ставим пробел и начинаем с большой буквы
        text = self.capitalizedSentence(text, '...')
        text = text.replace('...', '[3dot]')
        text = self.capitalizedSentence(text, '.')
        text = self.capitalizedSentence(text, '!')
        text = self.capitalizedSentence(text, '?')
        text = text.replace('[3dot]', '...')

        return text

    def capitalizedSentence(self, text, split_symbol):
        capitalized_text = u""
        # Заменяем троеточия
        sentences = text.split(split_symbol)

        if len(sentences) < 2:
            return text

        for sentence in text.split(split_symbol):
            sentence = sentence.strip()

            if len(sentence) == 0:
                continue

            if len(sentence) == 1:
                if split_symbol == ".":
                    capitalized_text += sentence
                    continue
                else:
                    sentence = sentence[0].capitalize()

            if len(sentence) > 1:
                sentence = sentence[0].capitalize() + sentence[1:len(sentence)]

            capitalized_text += sentence + u"%s " % split_symbol

        return capitalized_text

    def processText(self, text):

        text = text.replace('&', '&amp;')
        text = text.replace('<', '&lt;')
        text = text.replace ('>', '&gt;')

        SOAPBody  = '<?xml version="1.0" encoding="%s"?>\n' % self._encoding
        SOAPBody += '<soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">\n'
        SOAPBody += '<soap:Body>\n'
        SOAPBody += ' <ProcessText xmlns="http://typograf.artlebedev.ru/webservices/">\n'
        SOAPBody += '  <text>%s</text>\n' % text
        SOAPBody += '     <entityType>%s</entityType>\n' % self._entityType
        SOAPBody += '     <useBr>%s</useBr>\n' % self._useBr
        SOAPBody += '     <useP>%s</useP>\n' % self._useP
        SOAPBody += '     <maxNobr>%s</maxNobr>\n' % self._maxNobr 
        SOAPBody += '   </ProcessText>\n'
        SOAPBody += ' </soap:Body>\n'
        SOAPBody += '</soap:Envelope>\n'

        host = 'typograf.artlebedev.ru';
        SOAPRequest  = 'POST /webservices/typograf.asmx HTTP/1.1\n'
        SOAPRequest += 'Host: typograf.artlebedev.ru\n'
        SOAPRequest += 'Content-Type: text/xml\n'
        SOAPRequest += 'Content-Length: %d\n' % len(SOAPBody)
        SOAPRequest += 'SOAPAction: "http://typograf.artlebedev.ru/webservices/ProcessText"\n\n'

        SOAPRequest += SOAPBody


        remoteTypograf = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        remoteTypograf.connect((host, 80))
        remoteTypograf.sendall(SOAPRequest)

        typografResponse = ''
        while 1:
            buf = remoteTypograf.recv(8192)
            if len(buf)==0: break
            typografResponse += buf

        remoteTypograf.close()

        
        startsAt = typografResponse.find('<ProcessTextResult>') + 19
        endsAt = typografResponse.find('</ProcessTextResult>')
        typografResponse = typografResponse[startsAt:endsAt]


        typografResponse = typografResponse.replace('&amp;', '&' )
        typografResponse = typografResponse.replace('&lt;', '<')
        typografResponse = typografResponse.replace ('&gt;', '>')
        

        return  typografResponse


