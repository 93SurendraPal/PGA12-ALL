# from all_connections import database_cursor

# db_object = database_cursor('db_cms_fb','production')
# cursor = db_object.get_cursor()

# get_cities = "SELECT DISTINCT city_name FROM `city` where country = 'India' ORDER BY audience_size DESC LIMIT 100"
# cursor.execute(get_cities)
# cities_array = [val[0] for val in list(cursor.fetchall())]


def get_city_latlong(city_name):

        import requests,json
        base_url =  "https://maps.googleapis.com/maps/api/place/textsearch/json"
        prms = {'query':city_name,'key':'AIzaSyCHaTUur9Wnen4OXdb-o0IlldrYx8vW_Z4'}
        resp = requests.get(base_url,params=prms)
        result = json.loads(resp.text)
        try:
                main = result['results'][0]['geometry']['location']
        except:
                main = {'error':city,'result':result}

        return main

# main_array =  []
# for city in cities_array:
#         print city
#         row = {}
#         row['city'] = city
#         latlong = get_city_latlong(city)
#         if 'error' in latlong:
#                 print "error"
#                 print latlong
#                 continue
        
#         row['lat'] = latlong['lat']
#         row['lon'] = latlong['lng']
#         print row
#         main_array.append(row)
#         print main_array,'\n'


main_array = [{'lat': 28.6139391, 'city': 'New Delhi', 'lon': 77.2090212}, {'lat': 12.9715987, 'city': 'Bangalore', 'lon': 77.5945627}, {'lat': 22.572646, 'city': 'Calcutta', 'lon': 88.36389500000001}, {'lat': 18.5204303, 'city': 'Pune', 'lon': 73.8567437}, {'lat': 19.0759837, 'city': 'Mumbai', 'lon': 72.8776559}, {'lat': 17.385044, 'city': 'Hyderabad', 'lon': 78.486671}, {'lat': 26.8466937, 'city': 'Lucknow', 'lon': 80.94616599999999}, {'lat': 23.022505, 'city': 'Ahmedabad', 'lon': 72.5713621}, {'lat': 22.572646, 'city': 'Kolkata', 'lon': 88.36389500000001}, {'lat': 26.9124336, 'city': 'Jaipur', 'lon': 75.7872709}, {'lat': 22.7195687, 'city': 'Indore', 'lon': 75.8577258}, {'lat': 30.900965, 'city': 'Ludhiana', 'lon': 75.8572758}, {'lat': 25.5940947, 'city': 'Patna', 'lon': 85.1375645}, {'lat': 11.0509762, 'city': 'Malappuram', 'lon': 76.0710967}, {'lat': 13.0826802, 'city': 'Chennai', 'lon': 80.2707184}, {'lat': 26.1445169, 'city': 'Gauhati', 'lon': 91.7362365}, {'lat': 11.0168445, 'city': 'Coimbatore', 'lon': 76.9558321}, {'lat': 21.1702401, 'city': 'Surat', 'lon': 72.83106070000001}, {'lat': 20.2960587, 'city': 'Bhubaneswar', 'lon': 85.8245398}, {'lat': 27.1766701, 'city': 'Agra', 'lon': 78.00807449999999}, {'lat': 17.6868159, 'city': 'Visakhapatnam', 'lon': 83.2184815}, {'lat': 28.7040592, 'city': 'Delhi', 'lon': 77.10249019999999}, {'lat': 26.7271012, 'city': 'Siliguri', 'lon': 88.39528609999999}, {'lat': 28.4594965, 'city': 'Gurgaon', 'lon': 77.0266383}, {'lat': 9.9312328, 'city': 'Kochi', 'lon': 76.26730409999999}, {'lat': 21.1458004, 'city': 'Nagpur', 'lon': 79.0881546}, {'lat': 23.2599333, 'city': 'Bhopal', 'lon': 77.412615}, {'lat': 34.0836708, 'city': 'Srinagar', 'lon': 74.7972825}, {'lat': 28.5355161, 'city': 'Noida', 'lon': 77.3910265}, {'lat': 22.5957689, 'city': 'Howrah', 'lon': 88.26363940000002}, {'lat': 17.6868159, 'city': 'Vishakhapatnam', 'lon': 83.2184815}, {'lat': 26.449923, 'city': 'Kanpur', 'lon': 80.3318736}, {'lat': 19.0330488, 'city': 'Navi Mumbai (New Mumbai)', 'lon': 73.0296625}, {'lat': 30.7333148, 'city': 'Chandigarh', 'lon': 76.7794179}, {'lat': 22.3071588, 'city': 'Vadodara', 'lon': 73.1812187}, {'lat': 30.3781788, 'city': 'Ambala', 'lon': 76.7766974}, {'lat': 32.7266016, 'city': 'Jammu', 'lon': 74.8570259}, {'lat': 8.5241391, 'city': 'Trivandrum', 'lon': 76.9366376}, {'lat': 31.6339793, 'city': 'Amritsar', 'lon': 74.8722642}, {'lat': 31.1048145, 'city': 'Shimla', 'lon': 77.17340329999999}, {'lat': 28.9844618, 'city': 'Meerut City', 'lon': 77.7064137}, {'lat': 22.3038945, 'city': 'Rajkot', 'lon': 70.80215989999999}, {'lat': 28.4089123, 'city': 'Faridabad', 'lon': 77.3177894}, {'lat': 31.3260152, 'city': 'Jalandhar', 'lon': 75.57618289999999}, {'lat': 25.3176452, 'city': 'Varanasi', 'lon': 82.9739144}, {'lat': 30.3164945, 'city': 'Dehra Dun', 'lon': 78.03219179999999}, {'lat': 25.4358011, 'city': 'Allahabad', 'lon': 81.846311}, {'lat': 23.3440997, 'city': 'Ranchi', 'lon': 85.309562}, {'lat': 26.2389469, 'city': 'Jodhpur', 'lon': 73.02430939999999}, {'lat': 29.3909464, 'city': 'Panipat', 'lon': 76.9635023}, {'lat': 31.0445587, 'city': 'Nalagarh', 'lon': 76.70479040000001}, {'lat': 19.9974533, 'city': 'Nasik (Nashik)', 'lon': 73.78980229999999}, {'lat': 23.181467, 'city': 'Jabalpur', 'lon': 79.9864071}, {'lat': 26.2182871, 'city': 'Gwalior', 'lon': 78.18283079999999}, {'lat': 19.2183307, 'city': 'Thane', 'lon': 72.9780897}, {'lat': 21.2513844, 'city': 'Raipur', 'lon': 81.62964130000002}, {'lat': 16.5061743, 'city': 'Vijayawada', 'lon': 80.6480153}, {'lat': 9.9252007, 'city': 'Madurai', 'lon': 78.1197754}, {'lat': 19.1998211, 'city': 'Kandivali', 'lon': 72.84259399999999}, {'lat': 10.5276416, 'city': 'Trichur', 'lon': 76.2144349}, {'lat': 9.498066699999999, 'city': 'Alappuzha', 'lon': 76.3388484}, {'lat': 12.2958104, 'city': 'Mysore', 'lon': 76.6393805}, {'lat': 10.7904833, 'city': 'Tiruchirappalli', 'lon': 78.7046725}, {'lat': 30.3610314, 'city': 'Ambala Cantt', 'lon': 76.8485468}, {'lat': 12.9666662, 'city': 'Sriperumbudur', 'lon': 79.9465841}, {'lat': 19.8761653, 'city': 'Aurangabad', 'lon': 75.3433139}, {'lat': 10.7869994, 'city': 'Thanjavur', 'lon': 79.13782739999999}, {'lat': 8.183285699999999, 'city': 'Nagercoil', 'lon': 77.4118996}, {'lat': 29.6856929, 'city': 'Karnal', 'lon': 76.9904825}, {'lat': 29.4438165, 'city': 'Gorakhpur', 'lon': 75.67026469999999}, {'lat': 16.3066525, 'city': 'Guntur', 'lon': 80.4365402}, {'lat': 9.9252007, 'city': 'Mathurai', 'lon': 78.1197754}, {'lat': 22.8045665, 'city': 'Jamshedpur', 'lon': 86.2028754}, {'lat': 42.51954, 'city': 'Salem', 'lon': -70.8967155}, {'lat': 10.5276416, 'city': 'Thrissur', 'lon': 76.2144349}, {'lat': 18.5089197, 'city': 'Hadapsar', 'lon': 73.9260261}, {'lat': 12.9141417, 'city': 'Mangalore', 'lon': 74.8559568}, {'lat': 12.9165167, 'city': 'Vellore', 'lon': 79.13249859999999}, {'lat': 25.2138156, 'city': 'Kota', 'lon': 75.8647527}, {'lat': 28.8955152, 'city': 'Rohtak', 'lon': 76.606611}, {'lat': 23.6739452, 'city': 'Asansol', 'lon': 86.9523954}, {'lat': 28.3670355, 'city': 'Bareilly', 'lon': 79.4304381}, {'lat': 30.3397809, 'city': 'Patiala', 'lon': 76.3868797}, {'lat': 25.1785773, 'city': 'Maldah', 'lon': 88.24611829999999}, {'lat': 19.2869323, 'city': 'George Town', 'lon': -81.3674389}, {'lat': 40.7607793, 'city': 'Salt Lake City', 'lon': -111.8910474}, {'lat': 17.6302223, 'city': 'Medchal', 'lon': 78.4842132}, {'lat': 11.1085242, 'city': 'Tirupur', 'lon': 77.3410656}, {'lat': 17.4399295, 'city': 'Secunderabad', 'lon': 78.4982741}, {'lat': 28.4743879, 'city': 'Greater Noida', 'lon': 77.50399039999999}, {'lat': 11.2587531, 'city': 'Kozhikode', 'lon': 75.78041}, {'lat': 20.462521, 'city': 'Cuttack', 'lon': 85.8829895}, {'lat': 24.585445, 'city': 'Udaipur', 'lon': 73.712479}, {'lat': 30.7046486, 'city': 'Mohali', 'lon': 76.71787259999999}, {'lat': 16.9890648, 'city': 'Kakinada', 'lon': 82.2474648}, {'lat': 17.4947934, 'city': 'Kukatpally', 'lon': 78.3996441}, {'lat': 11.2587531, 'city': 'Calicut', 'lon': 75.78041}, {'lat': 15.8281257, 'city': 'Kurnool', 'lon': 78.0372792}, {'lat': 17.0005383, 'city': 'Rajahmundry', 'lon': 81.8040345}]


print len(main_array)

import pandas as pd
city_ltlng_tbl = pd.DataFrame(main_array)
city_ltlng_tbl.to_csv('/var/python/explore-flask/dao/city_latlongs.csv',index=False)
