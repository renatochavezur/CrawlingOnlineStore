# -*- coding: utf-8 -*-
import scrapy


class GeneralSpider(scrapy.Spider):
    name = 'general'
    allowed_domains = ['simple.ripley.com.pe']
    start_urls = ['https://simple.ripley.com.pe/navidad/']

    def parse(self, response):
        urls = response.css('div a::attr(href)').extract()
        
        for url in urls:
            url = response.urljoin(url)
            yield scrapy.Request(url=url, callback=self.parse_category)
        
        
    def parse_category(self, response):
        urls = response.css('div.catalog-container a::attr(href)').extract()
        
        for url in urls:
            url = response.urljoin(url)
            yield scrapy.Request(url=url, callback=self.parse_details)
        
        next_url = response.css('ul.pagination li a::attr(href)').extract()[-1]
        if '#' != next_url:
            next_url = response.urljoin(next_url)
            yield scrapy.Request(url=next_url, callback=self.parse)
        
    def parse_details(self,response):

        #Images
        imgs = response.css('ul.product-image-previews li img::attr(data-src)').extract()

        for img in imgs:
            img = response.urljoin(img)
        # / Images

        #Extras
        extras = response.css('section.product-extras section div div.content div.radio-item-options div.radio-item label')
        adicionales = []
        for extra in extras:
            plan = extra.css('span.radio-item__label::text').extract_first()
            precio = extra.css('span.radio-item__price::text').extract_first()
            adicionales.append({'plan': plan,'precio': precio})
        # / Extras

        #Entrega
        entregas = response.css('ul.product-shipping-details li')
        met_entrega =[]
        for entrega in entregas:
            if entrega.css('li.delivery-method::attr(class)').extract_first()=='delivery-method':
                met_entrega.append(entrega.css('span.product-shipping-name::text').extract_first())
        # / Entrega

        #Especificaciones
        tab_espec = response.css('div.accordion-item-wrapper div table tbody tr')
        especificaciones = []
        for espec in tab_espec:
            criterio = espec.css('td::text').extract()[0]
            data = espec.css('td::text').extract()[1]
            especificaciones.append({criterio: data})
        # / Especificaciones
        desc = response.css('p::text').extract()
        descripcion = ""
        for des in desc:
            descripcion += des
        yield{
            'Titulo': response.css('head title::text').extract_first(),
            'Marca': response.css('div.brand-logo span::text').extract_first(),
            'SKU': response.css('span.sku::text').extract_first(),
            'Descripcion': descripcion,
            'Precio-normal': response.css('li.product-normal-price span.product-price::text').extract_first(),
            'Precio-internet': response.css('li.product-internet-price span.product-price::text').extract_first(),
            'Descuento': response.css('li.product-price-discount span span.discount-percentage::text').extract_first(),
            'Puntos-ripley': response.css('li.product-ripley-puntos span.product-price::text').extract_first(),
            'Especificaciones': especificaciones,
            'Adicionales': adicionales,
            'Metodos-entrega':met_entrega,
            'images':imgs,
        }
