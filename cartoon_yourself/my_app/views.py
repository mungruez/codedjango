from django.shortcuts import render, redirect
from django.http import HttpResponse
from requests.compat import quote_plus
from bs4 import BeautifulSoup
from . import models
import requests
import xmltodict
from .forms import CartoonForm
import cv2
import openai
from django.http import JsonResponse
from .oai_queries import get_completion

openai.api_key = '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'
messages = [ {"role": "system", "content": "You are a intelligent assistant."} ]
BASE_CRAIGSLIST_URL = 'https://losangeles.craigslist.org/search/?query={}'
BASE_IMAGE_URL = 'https://images.craigslist.org/{}_300x300.jpg'

def home(request):
    if request.method == 'POST':
        prompt = request.POST.get('prompt')
        response = get_completion(prompt)
        print(response)
        return JsonResponse({'response': response})
    return render(request, 'base.html')

#def home(request):
    #return render(request, 'base.html')


def cartoon(request):
    context = {}
    if request.method == "POST":
        form = CartoonForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            final_cartoons = []
            #file = form.cleaned_data.get('cartoon_image')
            #image = cv2.imread("media/images/"+str(file.name))
            image = cv2.imread("media/images/"+form.cleaned_data['cartoon_image'].name)
            img_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            img_gray = cv2.medianBlur(img_gray, 5)
            edges = cv2.Laplacian(img_gray, cv2.CV_8U, ksize=5)
            ret, thresholded = cv2.threshold(edges, 70, 255, cv2.THRESH_BINARY_INV)
            cv2.imwrite('media/images/thresh.png', cv2.cvtColor(thresholded,
                                                                cv2.COLOR_GRAY2BGR))
            final_cartoons.append(('Sketch', 'media/images/thresh.png'))

            filtered = cv2.bilateralFilter(image, 10, 250, 250)
            cartoonized = cv2.bitwise_and(filtered, filtered, mask=thresholded)
            cv2.imwrite('media/images/cartoon.png',
                        cv2.stylization(image, sigma_s=60, sigma_r=0.07))
            final_cartoons.append(('Cartoonized', 'media/images/cartoon.png'))
            cartoons = models.Cartoon.objects.filter(name=form.cleaned_data.get('name'))
            for cartoon in cartoons:
                cartoon.delete()
            return render(request, 'my_app/display_cartoon_image.html', {'final_cartoons': final_cartoons})
    else:
        form = CartoonForm()
    context['form'] = form

    return render(request, 'my_app/cartoon.html', context)


def success(request):
    return HttpResponse('successfully uploaded')


def display_cartoon_image(request):

    return HttpResponse('successfully uploaded')


def jobs(request):
    return render(request, 'my_app/jobs.html')



def job_search(request):
    search = request.POST.get('search')
    models.Search.objects.create(search=search)
    page_num = 10
    job_error = 'NO_ERROR_FOUND'
    job_postings = []
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

    while page_num < 570:
        INDEED_URL = f'https://rss.indeed.com/rss?q={search}&l=California&start={page_num}'
        #INDEED_URL = f'https://rss.indeed.com/rss?q=Computer%20Internet&l=California&start={page_num}'
        try:
            data = requests.get(INDEED_URL , headers=headers)
        except:
            job_error = "ERROR_FOUND"
            break

        result = data.content.decode()
        x1=result.find("<item>")
        x2=result.find("</rss>")
        count=0
        mincount=95
        #dict1 = xmltodict.parse('<root>'+result[x1:x2-10]+'</root>', attr_prefix="")
        dict1=result[x1:x2-10].split("</item>")

        for item in dict1:
            jtitle = item.split("</title>")
            jsource = item.split("</source>")
            jdescription = item.split("</description>")
            jpubDate = item.split("</pubDate>")
            jlink = item.split("</link>")

            jtitle = jtitle[0].split("</title>")
            jtitle = jtitle[0][13:]

            jsource = jsource[0].split("</source>")
            x1=jsource[0].find("<source>")
            jsource = jsource[0]
            if x1 > -1:
                jsource=jsource[x1+8:]

            jdescription = jdescription[0].split("</description>")
            x1=jdescription[0].find("<description>")
            jdescription = jdescription[0].split("/a>")
            jdescription = jdescription[0]
            if x1 > -1:
                jdescription=jdescription[x1+13:]
            if len(jdescription) > 120:
                jdescription=jdescription[:120]
            jpubDate = jpubDate[0].split("</pubDate>")
            x1=jpubDate[0].find("<pubDate>")
            jpubDate = jpubDate[0]
            if x1 > -1:
                jpubDate=jpubDate[x1+9:]

            jlink = jlink[0].split("</link>")
            jlink = jlink[0].split(";from=rss")
            x1=jlink[0].find("<link>")
            jlink = jlink[0]
            if x1 > -1:
                jlink=jlink[x1+6:]
                
            job = {
                'title' : jtitle,
                'source' : jsource,
                'description' : jdescription,
                'pubDate' : jpubDate,
                'link' : jlink
            }

            if len(job['title']) > 7 and len(job['source']) > 7 and len(job['link']) > 12:
                if count<mincount or job['title'].find(search)>-1 or job['source'].find(search)>-1 or job['link'].find(search)>-1 or job['description'].find(search)>-1 : 
                    count=count+1
                    job_postings.append(job)      
        page_num += 10

    stuff_for_frontend = {
        'search': search,
        'job_postings': job_postings,
        'job_error': job_error
    }
    return render(request, 'my_app/job_search.html', stuff_for_frontend)


def new_search(request):
    search = request.POST.get('search')
    models.Search.objects.create(search=search)
    final_url = BASE_CRAIGSLIST_URL.format(quote_plus(search))
    response = requests.get(final_url)
    data = response.text
    soup = BeautifulSoup(data, features='html.parser')

    while True:
        message = input("User : ")
        if message: 
            messages.append({"role": "user", "content": message},)
        chat = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)
        reply = chat.choices[0].message.content
        print(f"ChatGPT: {reply}")
        messages.append({"role": "assistant", "content": reply})


    post_listings = soup.find_all('li', {'class': 'result-row'})
    final_postings = []
    print (data)
    for post in post_listings:
        post_title = post.find(class_='result-title').text
        post_url = post.find('a').get('href')

        if post.find(class_='result-price'):
            post_price = post.find(class_='result-price').text
        else:
            post_price = 'N/A'

        if post.find(class_='result-image').get('data-ids'):
            post_image_id = post.find(
                class_='result-image').get('data-ids').split(',')[0].split(':')[1]
            post_image_url = BASE_IMAGE_URL.format(post_image_id)
        else:
            post_image_url = 'https://craigslist.org/images/peace.jpg'

        final_postings.append(
            (post_title, post_url, post_price, post_image_url))

    stuff_for_frontend = {
        'search': search,
        'final_postings': final_postings,
    }

    return render(request, 'my_app/new_search.html', stuff_for_frontend)
