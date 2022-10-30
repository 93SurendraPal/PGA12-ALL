'''
TOP ORGANIC
$c_url="http://api.semrush.com/?type=domain_organic&key=17a82796751297a06f06c3ea6f0109df&display_limit=2"
            . "&export_columns=Ph,Nq,Tr&domain=".$related_domain."&database=".strtolower($country)
            ."&display_sort=tr_desc"

TOP PAID
$c_url="http://api.semrush.com/?type=domain_adwords&key=17a82796751297a06f06c3ea6f0109df&display_limit=2"
            . "&export_columns=Ph,Nq,Tr&domain=".$related_domain."&database=".strtolower($country)
            ."&display_sort=tr_desc";

TOP COMPETITORS
 $c_url="https://api.semrush.com/?type=domain_adwords_adwords&key=17a82796751297a06f06c3ea6f0109df&display_limit=5&export_columns=Dn,Cr,Np,Ad,At,Ac,Or"
                . "&domain=$related_domain&database=".strtolower($country_code);

WEBSITE TRAFFIC SOURCES & QUALITY
$c_url='curl -X POST http://api.semrush.com/analytics/ta/v1 -H "Content-Type:application/json" -d \'{"query": "{summary (actions: {domains:\"'.$related_domain.'\",geo:\"'.$country.'\"}) { items {report_date, domain, visits, bounce_rate, time_on_site, direct, referral, social, search }}}"}\'';

SITESPEED MOBILE FRIENDLINESS
 $c_url="https://www.googleapis.com/pagespeedonline/v2/runPagespeed?"
            . "key=AIzaSyAaBjLYCjayPAF4YO2p6iW1-sr4inXpvcs&screenshot=true&strategy=mobile&url=$brand_url";

'''
import requests
import json
import sys
import pandas as pd
from all_connections import database_cursor

class AssetWebsite():

        def __init__(self,domain,country_code):

                self.domain = 'https://' + domain
                self._domain = domain
                self.country_code = country_code

        def get_proxy(self):
                url = "https://gimmeproxy.com/api/getProxy"
                params = {
                        "post":"true",
                        "supportsHttps":"true",
                        "maxCheckPeriod": "3600"
                    }
                response = requests.get(url,params=params)
                response_jsn = json.loads(response.text)
                ip = response_jsn['ip']
                port = response_jsn['port']

                return ip,port

        def semrush_get_api(self,call_type,display_limit):
                import pandas as pd
                from StringIO import StringIO

                call_type_dict = {
                        'organic':'domain_organic',
                        'paid':'domain_adwords',
                        'competitors_paid':'domain_adwords_adwords',
                        'competitors_organic':'domain_organic_organic'
                    }
                export_columns_dict = {
                        'organic':'Ph,Nq,Tr',
                        'paid':'Ph,Nq,Tr',
                        'competitors_paid':'Dn,Cr,Np,Ad,At,Ac,Or,Ot',
                        'competitors_organic':'Dn,Cr,Np,Ad,At,Ac,Or,Ot'
                    }
                base_url = "http://api.semrush.com/"
                domain_format = self.domain.replace("https://","")
                params = {
                        "type":call_type_dict[call_type],
                        "key":"17a82796751297a06f06c3ea6f0109df",
                        "display_limit":display_limit,
                        "domain":domain_format,
                        "database":str(self.country_code).lower(),
                        "export_columns":export_columns_dict[call_type]
                    }
                response = requests.get(base_url,params=params)
                out_tbl = pd.read_csv(StringIO(response.text),sep=';')
                out_jsn = out_tbl.to_dict(orient='records')

                return out_jsn

        def semrush_post_api(self):
                '''deprecated by semrush'''
                base_url = "https://api.semrush.com/analytics/ta/v1"
                domain_format = self.domain.replace('https://','')
                heads = {"Content-Type":"application/json",'Host':'api.semrush.com','Accept':'application/json, text/plain, */*'}
                data = '{"query":"{summary  (actions:    {      domains:[\\\"'+domain_format+ '\\\"],geo:\\\"IN\\\",    } )  {    items { bounce_rate, domain, rank, report_date, visits, users, direct, referral, social, search, paid, time_on_site }  }}"}'
                response = requests.post(base_url,headers=heads,data=data)
                print response.url
                api_out = json.loads(response.text)
                vals = api_out['data']['summary']['items']

                return vals


        def siteSpeed_mobFriend_api(self):

                base_url = "https://www.googleapis.com/pagespeedonline/v2/runPagespeed"
                params = {"key":"AIzaSyAaBjLYCjayPAF4YO2p6iW1-sr4inXpvcs","screenshot":"true","strategy":"mobile","url":self.domain}
                response = requests.get(base_url,params=params)
                print response.url

                output_jsn = json.loads(response.text)

                try:
                        sitespeed = output_jsn['ruleGroups']['SPEED']['score']
                        usability = output_jsn['ruleGroups']['USABILITY']['score']
                        base64img = output_jsn['screenshot']['data']
                except:
                        sitespeed = output_jsn
                        usability = {'error':'refer sitespeed'}
                
                return sitespeed,usability

        def sitespy_api(self):
                # base_url = "http://sitespy.xeroneit.net/native_api/similar_web_check"
                base_url = "https://dandatalab.com/sitespy/native_api/similar_web_check"
                domain_format = self.domain.replace('https://','http://')
                 
                ip,port = self.get_proxy()
                proxyDict = {
                        'http':'http://' + str(ip) + ':' + str(port),
                        'https':'https://' + str(ip) + ':' + str(port)
                    }
                params = {"api_key":"1-RWe03UL1527163447tIbHRPg","domain":self.domain}
                response = requests.get(base_url,params=params,proxies=proxyDict)
                
                output_jsn = json.loads(response.text)

                if output_jsn['status'] == 'success':
                        top_referral = output_jsn['top_referral_site']
                        organic_search_perc = output_jsn['organic_search_percentage']
                        paid_search_perc = output_jsn['paid_search_percentage']
                        social_sites = output_jsn['social_site_name']
                        social_site_perc = output_jsn['social_site_percentage']
                        social_site_traffic = {social_sites[index]:social_site_perc[index] for index in range(len(social_sites))}
                        output = {'top_referral_sites':top_referral,'organic_search_percentage':organic_search_perc,'paid_search_percentage':paid_search_perc,'social_site_traffic':social_site_traffic}
                else:
                        output = {'error':'sitespy_failed'}

                return output

        def alexa_siteinfo(self):
                from trends_main import Browser
                url = self.domain_format()

        def organic_paid_kws(self,in_data):
                kw_tbl = pd.DataFrame(in_data)
                kw_list = kw_tbl.groupby(['Keyword'])[['Search Volume']].sum().reset_index()
                kw_list = kw_list.sort_values('Search Volume',ascending=False).head(10)['Keyword'].tolist()

                final_out = []
                for word in kw_list:
                        kw_sub = kw_tbl.loc[kw_tbl['Keyword']==word,]
                        kw_sub = kw_sub.groupby(['Keyword','type'])[['Search Volume','Traffic (%)']].max().reset_index()

                        word_result = {}
                        word_result['keyword'] = word
                        for i,row in kw_sub.iterrows():
                                word_result.update({row['type']:[row['Search Volume'],row['Traffic (%)']]})

                        final_out.append(word_result)

                return final_out

        def competitor_organic_paid(self,in_data):
                main_tbl = pd.DataFrame(in_data)
                main_tbl_sub = main_tbl[['Domain','Organic Traffic','Adwords Traffic','type']]
                main_tbl_sub['total_traffic'] = main_tbl_sub['Organic Traffic'] + main_tbl_sub['Adwords Traffic']
                domain_list = main_tbl_sub.groupby(['Domain'])[['total_traffic']].sum().reset_index()
                domain_list = domain_list.sort_values('total_traffic',ascending=False).head(10)['Domain'].tolist()

                final_out = []
                for domain in domain_list:
                        domain_sub = main_tbl_sub.loc[main_tbl_sub['Domain']==domain,]
                        domain_row = {}
                        domain_row['domain'] = domain
                        for ind,row in domain_sub.iterrows():
                                domain_row.update({'organic':row['Organic Traffic'],'paid':row['Adwords Traffic']})

                        final_out.append(domain_row)

                return final_out

        def run_keywords(self):
                call_type_dict = {'organic':'domain_organic','paid':'domain_adwords'}
                calls = call_type_dict.keys()
                final_out = {}
                keyword_formatting = []
                for call in calls:
                        output = self.semrush_get_api(call,20)                        
                        [r.update({'type':call}) for r in output]
                        keyword_formatting += output

                kw_result = self.organic_paid_kws(keyword_formatting)

                result = json.dumps(kw_result)
                return result


        def run_competitors(self):
                call_type_dict = {
                        'competitors_paid':'domain_adwords_adwords',
                        'competitors_organic':'domain_organic_organic'
                    }
                calls = call_type_dict.keys()
                final_out = {}
                competitor_formatting = []
                for call in calls:
                        # print call
                        output = self.semrush_get_api(call,20)
                        # output = competitor_output[call]
                        [r.update({'type':call.replace('competitors_','')}) for r in output]
                        competitor_formatting += output
                        # print output,'\n'
                        continue

                competitor_result = self.competitor_organic_paid(competitor_formatting)
                result = json.dumps(competitor_result)
                return result

        def run_sitespeed_usability(self):

                sitespy_out = self.sitespy_api()
                sitespeed,usability = self.siteSpeed_mobFriend_api()
                output = {
                        'inbound_data':sitespy_out,
                        'site_speed':sitespeed,
                        'usability':usability
                    }

                output_jsn = json.dumps(output)
                return output_jsn

        def run_traffic_sources(self):

                traffic_quality = self.semrush_post_api()
                output = {
                        'traffic_sources':traffic_quality
                    }

                output_jsn = json.dumps(output)
                return output_jsn


        def run_age_gender_split(self):
                age_mapper = [[6,14 , 'Male'],[6,14 , 'Female'],[15,24,'Female'],[15,24 , 'Male'],[25,34,'Female'],[25,34,'Male'],[35,44,'Female'],[35,44,'Male'],[45,99,'Female'], [45,99,'Male']]
                domain_format = self.domain.replace("https://","")
                domain_country = self.country_code
                db_object = database_cursor('explore','dev')
                final_df = []
                fetch_category_q = "SELECT DISTINCT(Category_1) FROM `comscore_websites` where Media LIKE '%"+domain_format+"%' LIMIT 1" 
                category_res = db_object.execute_one(fetch_category_q)
                if(category_res != None):
                    final_df = pd.DataFrame()
                    category_res = category_res[0]

                    for i in age_mapper:

                        website_query = "SELECT age_min, age_max, gender, SUM(`Total Unique Visitors (000)`),`% Composition Unique Visitors`, `Composition Index UV`, media FROM comscore_websites cw LEFT JOIN db_cms_fb.TBL_COUNTRIES c ON cw.country = c.name WHERE age_min= "+str(i[0])+" AND age_max= "+str(i[1])+" AND gender ='"+i[2]+"' AND media LIKE '%"+domain_format+"%' AND c.sortname LIKE '"+domain_country+"' GROUP by Media" 
                        sql_output = {}
                        sql_output = db_object.execute(website_query)
                        output_result = pd.DataFrame.from_records(list(sql_output), columns = ['age_min', 'age_max', 'gender', 'visitors', 'affinity', 'composite_index', 'name']) # 'views', 'affinity', 'composite_index' => `Total Unique Visitors (000)`,`% Composition Unique Visitors`, `Composition Index UV`
                        output_result[['visitors', 'affinity', 'composite_index']] = output_result[['visitors', 'affinity', 'composite_index']].astype(float)
                        overall_query = "SELECT SUM(`Total Unique Visitors (000)`) FROM comscore_websites cw LEFT JOIN db_cms_fb.TBL_COUNTRIES c ON cw.country = c.name WHERE age_min= "+str(i[0])+" AND age_max= "+str(i[1]) +" AND gender='"+i[2]+"' AND Category_1 = 'Retail' GROUP BY Category_1" 
                        div_output = {}
                        div_output = db_object.execute(overall_query)
                        output_result['views'] = output_result['visitors'] / float(div_output[0][0])

                        final_df = final_df.append(output_result, ignore_index=True)
                        # print final_df
                    final_df = final_df.to_dict(orient='records')  
                return final_df


        def run(self):
                call_type_dict = {'organic':'domain_organic','paid':'domain_adwords','competitors_paid':'domain_adwords_adwords','competitors_organic':'domain_organic_organic'}
                calls = call_type_dict.keys()
                final_out = {}
                keyword_formatting = []
                competitor_formatting = []
                # output = self.semrush_get_api('paid',5)
                # print output
                # sys.exit()
                
                
                # sitespy_out = self.sitespy_api()
                # sitespeed,usability = self.siteSpeed_mobFriend_api()
                
                # traffic_quality = self.semrush_post_api()
                # final_out['traffic_sources'] = traffic_quality
                # final_out['site_speed'] = sitespeed
                # final_out['usability'] = usability
                # final_out['inbound_data'] = sitespy_out
                # kw_output = {'organic':[{'Traffic (%)': 30.48, 'Keyword': 'nykaa', 'Search Volume': 550000}, {'Traffic (%)': 1.5, 'Keyword': 'nykaa com', 'Search Volume': 27100}, {'Traffic (%)': 1.19, 'Keyword': 'kajal', 'Search Volume': 368000}, {'Traffic (%)': 1.07, 'Keyword': 'lakme lipstick', 'Search Volume': 33100}, {'Traffic (%)': 0.67, 'Keyword': 'nayka', 'Search Volume': 12100}, {'Traffic (%)': 0.67, 'Keyword': 'www nykaa com', 'Search Volume': 12100}, {'Traffic (%)': 0.58, 'Keyword': 'lipstick shades', 'Search Volume': 18100}, {'Traffic (%)': 0.48, 'Keyword': 'lakme cc cream', 'Search Volume': 14800}, {'Traffic (%)': 0.43, 'Keyword': 'makeup kit', 'Search Volume': 90500}, {'Traffic (%)': 0.39, 'Keyword': 'nykaa lipstick', 'Search Volume': 12100}, {'Traffic (%)': 0.39, 'Keyword': 'nykaa sale', 'Search Volume': 12100}, {'Traffic (%)': 0.39, 'Keyword': 'lakme 9 to 5', 'Search Volume': 12100}, {'Traffic (%)': 0.35, 'Keyword': 'hair straightener', 'Search Volume': 74000}, {'Traffic (%)': 0.33, 'Keyword': 'kajal', 'Search Volume': 368000}, {'Traffic (%)': 0.32, 'Keyword': 'lakme 9to5 lipstick', 'Search Volume': 9900}, {'Traffic (%)': 0.32, 'Keyword': 'lakme lip crayon', 'Search Volume': 9900}, {'Traffic (%)': 0.32, 'Keyword': 'highlighter', 'Search Volume': 9900}, {'Traffic (%)': 0.32, 'Keyword': 'elle 18 lipstick', 'Search Volume': 9900}, {'Traffic (%)': 0.32, 'Keyword': 'lip gloss', 'Search Volume': 9900}, {'Traffic (%)': 0.32, 'Keyword': 'mascara', 'Search Volume': 9900}],'paid':[{'Traffic (%)': 15.84, 'Keyword': 'nykaa', 'Search Volume': 550000}, {'Traffic (%)': 10.6, 'Keyword': 'makeup', 'Search Volume': 368000}, {'Traffic (%)': 4.38, 'Keyword': 'nykaa', 'Search Volume': 550000}, {'Traffic (%)': 3.03, 'Keyword': 'nykaa', 'Search Volume': 550000}, {'Traffic (%)': 2.93, 'Keyword': 'makeup', 'Search Volume': 368000}, {'Traffic (%)': 2.35, 'Keyword': 'nykaa', 'Search Volume': 550000}, {'Traffic (%)': 1.74, 'Keyword': 'wow', 'Search Volume': 60500}, {'Traffic (%)': 1.68, 'Keyword': 'nykaa', 'Search Volume': 550000}, {'Traffic (%)': 1.68, 'Keyword': 'nykaa', 'Search Volume': 550000}, {'Traffic (%)': 1.66, 'Keyword': 'makeup games', 'Search Volume': 301000}, {'Traffic (%)': 1.34, 'Keyword': 'nykaa', 'Search Volume': 550000}, {'Traffic (%)': 1.12, 'Keyword': 'makeup', 'Search Volume': 368000}, {'Traffic (%)': 0.95, 'Keyword': 'bio oil', 'Search Volume': 33100}, {'Traffic (%)': 0.9, 'Keyword': 'makeup', 'Search Volume': 368000}, {'Traffic (%)': 0.78, 'Keyword': 'nykaa com', 'Search Volume': 27100}, {'Traffic (%)': 0.78, 'Keyword': 'mac lipstick', 'Search Volume': 27100}, {'Traffic (%)': 0.7, 'Keyword': 'nail art', 'Search Volume': 165000}, {'Traffic (%)': 0.67, 'Keyword': 'makeup', 'Search Volume': 368000}, {'Traffic (%)': 0.63, 'Keyword': 'huda beauty', 'Search Volume': 22200}, {'Traffic (%)': 0.52, 'Keyword': 'avon', 'Search Volume': 18100}]}
                competitor_output = {'competitors_organic':[{'Domain': 'purplle.com', 'Organic Traffic': 326537, 'Adwords Cost': 1046, 'Adwords Keywords': 1177, 'Organic Keywords': 34325, 'Adwords Traffic': 15079, 'Common Keywords': 5638, 'Competitor Relevance': 22.51}, {'Domain': 'makeupandbeauty.com', 'Organic Traffic': 315112, 'Adwords Cost': 0, 'Adwords Keywords': 0, 'Organic Keywords': 44045, 'Adwords Traffic': 0, 'Common Keywords': 5503, 'Competitor Relevance': 14.51}, {'Domain': 'vanitynoapologies.com', 'Organic Traffic': 140899, 'Adwords Cost': 0, 'Adwords Keywords': 0, 'Organic Keywords': 25502, 'Adwords Traffic': 0, 'Common Keywords': 3367, 'Competitor Relevance': 11.84}, {'Domain': 'wiseshe.com', 'Organic Traffic': 76810, 'Adwords Cost': 0, 'Adwords Keywords': 0, 'Organic Keywords': 26034, 'Adwords Traffic': 0, 'Common Keywords': 1858, 'Competitor Relevance': 9.33}, {'Domain': 'priceline.com.au', 'Organic Traffic': 9671, 'Adwords Cost': 2, 'Adwords Keywords': 4, 'Organic Keywords': 16591, 'Adwords Traffic': 13, 'Common Keywords': 1733, 'Competitor Relevance': 8.86}, {'Domain': 'tipsandbeauty.com', 'Organic Traffic': 116537, 'Adwords Cost': 0, 'Adwords Keywords': 0, 'Organic Keywords': 13594, 'Adwords Traffic': 0, 'Common Keywords': 1876, 'Competitor Relevance': 8.81}, {'Domain': 'ulta.com', 'Organic Traffic': 85917, 'Adwords Cost': 0, 'Adwords Keywords': 2, 'Organic Keywords': 22661, 'Adwords Traffic': 1, 'Common Keywords': 2458, 'Competitor Relevance': 8.29}, {'Domain': 'newu.in', 'Organic Traffic': 7221, 'Adwords Cost': 0, 'Adwords Keywords': 0, 'Organic Keywords': 4920, 'Adwords Traffic': 0, 'Common Keywords': 1201, 'Competitor Relevance': 7.44}, {'Domain': 'beautyglimpse.com', 'Organic Traffic': 81872, 'Adwords Cost': 0, 'Adwords Keywords': 0, 'Organic Keywords': 16935, 'Adwords Traffic': 0, 'Common Keywords': 1479, 'Competitor Relevance': 6.95}, {'Domain': 'superdrug.com', 'Organic Traffic': 75263, 'Adwords Cost': 0, 'Adwords Keywords': 3, 'Organic Keywords': 27786, 'Adwords Traffic': 10, 'Common Keywords': 1526, 'Competitor Relevance': 6.44}, {'Domain': 'indianbeautyhub.com', 'Organic Traffic': 104526, 'Adwords Cost': 0, 'Adwords Keywords': 0, 'Organic Keywords': 9057, 'Adwords Traffic': 0, 'Common Keywords': 1074, 'Competitor Relevance': 6.29}, {'Domain': 'thebodyshop.in', 'Organic Traffic': 104611, 'Adwords Cost': 410, 'Adwords Keywords': 623, 'Organic Keywords': 3772, 'Adwords Traffic': 8930, 'Common Keywords': 956, 'Competitor Relevance': 5.68}, {'Domain': 'makeupalley.com', 'Organic Traffic': 17044, 'Adwords Cost': 0, 'Adwords Keywords': 0, 'Organic Keywords': 19108, 'Adwords Traffic': 0, 'Common Keywords': 1327, 'Competitor Relevance': 5.51}, {'Domain': 'bigbasket.com', 'Organic Traffic': 1556053, 'Adwords Cost': 6440, 'Adwords Keywords': 554, 'Organic Keywords': 50234, 'Adwords Traffic': 48813, 'Common Keywords': 1463, 'Competitor Relevance': 5.04}, {'Domain': 'sephora.com', 'Organic Traffic': 209768, 'Adwords Cost': 3, 'Adwords Keywords': 3, 'Organic Keywords': 28171, 'Adwords Traffic': 25, 'Common Keywords': 1378, 'Competitor Relevance': 4.93}, {'Domain': 'feelunique.com', 'Organic Traffic': 7770, 'Adwords Cost': 4, 'Adwords Keywords': 8, 'Organic Keywords': 7850, 'Adwords Traffic': 71, 'Common Keywords': 898, 'Competitor Relevance': 4.92}, {'Domain': 'totalbeauty.com', 'Organic Traffic': 89210, 'Adwords Cost': 0, 'Adwords Keywords': 0, 'Organic Keywords': 20582, 'Adwords Traffic': 0, 'Common Keywords': 1374, 'Competitor Relevance': 4.75}, {'Domain': 'maybelline.com', 'Organic Traffic': 218478, 'Adwords Cost': 0, 'Adwords Keywords': 0, 'Organic Keywords': 5641, 'Adwords Traffic': 0, 'Common Keywords': 783, 'Competitor Relevance': 4.57}, {'Domain': 'lakmeindia.com', 'Organic Traffic': 196706, 'Adwords Cost': 8275, 'Adwords Keywords': 1017, 'Organic Keywords': 3849, 'Adwords Traffic': 27768, 'Common Keywords': 715, 'Competitor Relevance': 4.54}, {'Domain': 'maccosmetics.com', 'Organic Traffic': 125218, 'Adwords Cost': 0, 'Adwords Keywords': 0, 'Organic Keywords': 5650, 'Adwords Traffic': 0, 'Common Keywords': 751, 'Competitor Relevance': 4.4}],'competitors_paid':[{'Domain': 'purplle.com', 'Organic Traffic': 326537, 'Adwords Cost': 1046, 'Adwords Keywords': 1177, 'Organic Keywords': 34325, 'Adwords Traffic': 15079, 'Common Keywords': 111, 'Competitor Relevance': 2.57}, {'Domain': 'reduto.in', 'Organic Traffic': 0, 'Adwords Cost': 3960, 'Adwords Keywords': 1953, 'Organic Keywords': 0, 'Adwords Traffic': 36997, 'Common Keywords': 40, 'Competitor Relevance': 0.87}, {'Domain': 'herbalforhealth.co.in', 'Organic Traffic': 19172, 'Adwords Cost': 1372, 'Adwords Keywords': 452, 'Organic Keywords': 781, 'Adwords Traffic': 9894, 'Common Keywords': 34, 'Competitor Relevance': 0.83}, {'Domain': 'bebeautiful.in', 'Organic Traffic': 51836, 'Adwords Cost': 18014, 'Adwords Keywords': 4900, 'Organic Keywords': 15805, 'Adwords Traffic': 124813, 'Common Keywords': 67, 'Competitor Relevance': 0.82}, {'Domain': 'thebodyshop.in', 'Organic Traffic': 104611, 'Adwords Cost': 410, 'Adwords Keywords': 623, 'Organic Keywords': 3772, 'Adwords Traffic': 8930, 'Common Keywords': 30, 'Competitor Relevance': 0.7}, {'Domain': 'lakmeindia.com', 'Organic Traffic': 196706, 'Adwords Cost': 8275, 'Adwords Keywords': 1017, 'Organic Keywords': 3849, 'Adwords Traffic': 27768, 'Common Keywords': 27, 'Competitor Relevance': 0.64}, {'Domain': 'flipkart.com', 'Organic Traffic': 51968781, 'Adwords Cost': 175695, 'Adwords Keywords': 54366, 'Organic Keywords': 1096243, 'Adwords Traffic': 3733374, 'Common Keywords': 589, 'Competitor Relevance': 0.59}, {'Domain': 'herbalforliving.com', 'Organic Traffic': 0, 'Adwords Cost': 17, 'Adwords Keywords': 78, 'Organic Keywords': 58, 'Adwords Traffic': 193, 'Common Keywords': 21, 'Competitor Relevance': 0.57}, {'Domain': 'jabong.com', 'Organic Traffic': 3492331, 'Adwords Cost': 15709, 'Adwords Keywords': 9804, 'Organic Keywords': 151495, 'Adwords Traffic': 210719, 'Common Keywords': 102, 'Competitor Relevance': 0.54}, {'Domain': 'cleanandclear.in', 'Organic Traffic': 20633, 'Adwords Cost': 9140, 'Adwords Keywords': 3596, 'Organic Keywords': 1013, 'Adwords Traffic': 41514, 'Common Keywords': 41, 'Competitor Relevance': 0.51}, {'Domain': 'gillette.co.in', 'Organic Traffic': 107535, 'Adwords Cost': 2870, 'Adwords Keywords': 1613, 'Organic Keywords': 1864, 'Adwords Traffic': 14516, 'Common Keywords': 28, 'Competitor Relevance': 0.51}, {'Domain': 'shopclues.com', 'Organic Traffic': 5323944, 'Adwords Cost': 8899, 'Adwords Keywords': 15163, 'Organic Keywords': 427780, 'Adwords Traffic': 311469, 'Common Keywords': 171, 'Competitor Relevance': 0.42}, {'Domain': 'stuccu.com', 'Organic Traffic': 36, 'Adwords Cost': 64583, 'Adwords Keywords': 65312, 'Organic Keywords': 141, 'Adwords Traffic': 470962, 'Common Keywords': 46, 'Competitor Relevance': 0.42}, {'Domain': 'philips.co.in', 'Organic Traffic': 668981, 'Adwords Cost': 8155, 'Adwords Keywords': 2319, 'Organic Keywords': 25295, 'Adwords Traffic': 30166, 'Common Keywords': 19, 'Competitor Relevance': 0.41}, {'Domain': 'ebay.in', 'Organic Traffic': 3709928, 'Adwords Cost': 17325, 'Adwords Keywords': 20096, 'Organic Keywords': 413989, 'Adwords Traffic': 391326, 'Common Keywords': 85, 'Competitor Relevance': 0.4}, {'Domain': 'shoppersstop.com', 'Organic Traffic': 947235, 'Adwords Cost': 3884, 'Adwords Keywords': 1929, 'Organic Keywords': 73798, 'Adwords Traffic': 50279, 'Common Keywords': 19, 'Competitor Relevance': 0.4}, {'Domain': 'rougesalons.com', 'Organic Traffic': 124, 'Adwords Cost': 0, 'Adwords Keywords': 21, 'Organic Keywords': 23, 'Adwords Traffic': 7, 'Common Keywords': 14, 'Competitor Relevance': 0.38}, {'Domain': 'iherb.com', 'Organic Traffic': 42376, 'Adwords Cost': 22205, 'Adwords Keywords': 6576, 'Organic Keywords': 21503, 'Adwords Traffic': 128920, 'Common Keywords': 18, 'Competitor Relevance': 0.34}, {'Domain': 'healthkart.com', 'Organic Traffic': 470167, 'Adwords Cost': 5109, 'Adwords Keywords': 2463, 'Organic Keywords': 33693, 'Adwords Traffic': 45213, 'Common Keywords': 23, 'Competitor Relevance': 0.32}, {'Domain': 'netmeds.com', 'Organic Traffic': 438689, 'Adwords Cost': 21617, 'Adwords Keywords': 2083, 'Organic Keywords': 22105, 'Adwords Traffic': 72945, 'Common Keywords': 17, 'Competitor Relevance': 0.32}]}


                for call in calls:
                        if call in ['organic','paid']:
                                # output = self.semrush_get_api(call,20)
                                # print output,'\n'
                                continue
                                output = kw_output[call]
                                [r.update({'type':call}) for r in output]
                                keyword_formatting += output
                        else:
                                # print call
                                # output = self.semrush_get_api(call,20)
                                output = competitor_output[call]
                                [r.update({'type':call.replace('competitors_','')}) for r in output]
                                competitor_formatting += output
                                # print output,'\n'
                                continue

                competitor_result = self.competitor_organic_paid(competitor_formatting)
                print json.dumps(competitor_result)
                sys.exit()
                # kw_result = self.organic_paid_kws(keyword_formatting)

                result = json.dumps(kw_result)
                return result





if __name__ == "__main__":

        obj = AssetWebsite("nykaa.com","in")
        # sitespeed,usability = obj.siteSpeed_mobFriend_api()
        # output = obj.semrush_post_api()
        # output = obj.run_sitespeed_usability()
        output = obj.run_age_gender_split()
        print output
