import requests
import requests_cache



requests_cache.install_cache(cache_name = 'image_cache', backend='sqlite', expire_after=900)




def get_image(search):

    url = "https://google-search72.p.rapidapi.com/imagesearch"

    querystring = {"q": search,"gl":"us","lr":"lang_en","num":"1","start":"0"}

    headers = {
        "X-RapidAPI-Key": "42fd925984msh562e14a38e46f74p1d7d82jsnc9f5517ec678",
        "X-RapidAPI-Host": "google-search72.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)

    data = response.json()
    print(data)
    img_url = data['items'][0]['originalImageUrl'] #traversing data dictionary to get the image url we want
    return img_url

def calc_roi(purch_price, exp_total, income_total):
    initial_invest = (purch_price + exp_total)
    profit = income_total - initial_invest
    roi = profit / initial_invest
    return roi


#  for prop in properties:
#         exp_total = db.session.execute(text(f'select sum(amount) from expense inner join property on property.prop_id = expense.prop_id where expense.user_id = {current_user.user_id}'))
#         inc_total = db.session.execute(text(f'select sum(amount) from income inner join property on property.prop_id = income.prop_id where income.user_id = {current_user.user_id}'))
#         roi= calc_roi(prop[2],exp_total.all()[0][0],inc_total.all()[0][0])
#         roi = roi*100
#         roi_f = "%.2f" % roi+"%"
#         rois.append(roi_f)