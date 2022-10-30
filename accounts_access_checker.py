import pandas as pd
import requests

class FbAccountAccessChecker():
	
	
	def __init__(self):

		from ..essentials.all_connections import mongo
		import datetime

		# mongo_service = mongo('mongo_main')
		# mongo_client = mongo_service.get_client()
		# db = mongo_client["dandatalab"]
		# current_date = str(datetime.date.today()).split(' ')[0]
		# self.Table = db.get_collection("lasersight_output")

	def run(self,buss_id):
		raw_fb_data = self.raw_fb_users_data(buss_id)
		# raw_fb_data.to_csv('tmp_raw_fb_data.csv')
		#raw_fb_data=pd.read_csv('tmp_raw_fb_data.csv')
		raw_ad_data = self.raw_ad_data()
		raw_domain_data = self.raw_domain_data()

		access_revoke_df = raw_fb_data[~raw_fb_data.email.isin(list(raw_ad_data['email']))]
		access_revoke_df.drop(['employee_name','company_domain'],axis=1,inplace=True)
		#access_revoke_df = pd.read_csv('tmp_access_revoke_df.csv')
		#access_revoke_df.drop(['Unnamed: 0'],axis=1,inplace=True)
		print access_revoke_df
		#access_revoke_df.to_csv('tmp_access_revoke_df.csv')

		admin_data = raw_fb_data[raw_fb_data['role']=='ADMIN']
		admin_data = list(admin_data['email'].unique())
		#admin_data = len(admin_data)
		print admin_data

		not_company_domain = raw_fb_data[~raw_fb_data.company_domain.isin(list(raw_domain_data['company_domain']))]
		not_company_domain = list(not_company_domain['email'].unique())
		
		mail_shoot = self.send_emails(access_revoke_df,admin_data,not_company_domain)

		return access_revoke_df,admin_data,not_company_domain

	def raw_fb_users_data(self,buss_id):
		import time
		from facebook_business.api import FacebookAdsApi
		from facebook_business.adobjects.business import Business
		from ..essentials.all_connections import facebook_gautam
		from facebook_business.adobjects.adaccount import AdAccount

		token,version=facebook_gautam().main()

		FacebookAdsApi.init(access_token=token)

		buss_obj = Business(buss_id)
		buss_obj = buss_obj.get_business_users(fields={'id','role','name','email','assigned_ad_accounts','assigned_pages'},params={'limit':1})

		final_access_data = []
		
		for data in buss_obj:
		    time.sleep(4)
		    try:
		        for assigned_ad_accounts_data in data['assigned_ad_accounts']['data']:
		            time.sleep(1)
		            try:
		                dct = {}
		                dct['tasks'] = assigned_ad_accounts_data['tasks']
		                dct['type_id'] = assigned_ad_accounts_data['account_id']
		                dct['type_name'] = ''
		                dct['id'] = data['id']
		                dct['name'] = data['name']
		                dct['role'] = data['role']
		                dct['email'] = data['email']
		                dct['type'] = 'account'
		                final_access_data.append(dct)
		            except Exception as ex:
		                print ex
		        for assigned_ad_accounts_data in data['assigned_pages']['data']:
		            time.sleep(1)
		            try:
		                dct = {}
		                dct['tasks'] = assigned_ad_accounts_data['tasks']
		                dct['type_id'] = assigned_ad_accounts_data['id']
		                dct['type_name'] = assigned_ad_accounts_data['name']
		                dct['id'] = data['id']
		                dct['name'] = data['name']
		                dct['role'] = data['role']
		                dct['email'] = data['email']
		                dct['type'] = 'page'
		                final_access_data.append(dct)
		            except Exception as ex:
		                print ex
		        if not data['assigned_pages']['data'] or data['assigned_ad_accounts']['data']:
		            time.sleep(1)
		            dct = {}
		            dct['id'] = data['id']
		            try:
		                dct['name'] = data['name']
		            except:
		                pass
		            dct['role'] = data['role']
		            dct['email'] = data['email']
		            final_access_data.append(dct)
		    except:
		        pass

		final_access_data_df = pd.DataFrame(final_access_data)
		final_access_data_df.fillna('na',inplace=True)
		final_access_data_df['email'] = final_access_data_df['email'].str.lower()
		final_access_data_df['tasks'] = final_access_data_df['tasks'].apply(lambda x : tuple(x) if type(x) is list else x)
		final_access_data_df['employee_name'],final_access_data_df['company_domain'] = zip(*final_access_data_df["email"].str.split('@').tolist())
		final_access_data_df.drop_duplicates(keep='first',inplace=True)

		account_id_list = {}
		account_list = list(final_access_data_df['type_id'].unique())
		for act_ in account_list:
		    data = AdAccount(str('act_')+str(act_))
		    try:
		        data_tp = data.api_get(fields={'name'})
		        account_id_list[act_]=data_tp['name']
		    except:
		        pass

		for i in range(1,len(final_access_data_df)):
		    if final_access_data_df.loc[i,'type'] == 'account':
		        final_access_data_df.loc[i,'type_name'] = account_id_list[final_access_data_df.loc[i,'type_id']]

		return final_access_data_df

	def raw_ad_data(self):

		from ..essentials.all_connections import database_cursor
		self.db_obj_db_cms_fb = database_cursor('db_cms_fb','dev')

		query = "SELECT DISTINCT mail FROM `AD_Dump`"

		fetch_accounts = self.db_obj_db_cms_fb.execute(query)

		fetch_accounts = pd.DataFrame(list(fetch_accounts))
		fetch_accounts.columns = ['email']

		fetch_accounts['email'] = fetch_accounts['email'].str.lower()

		print fetch_accounts

		return fetch_accounts

	def raw_domain_data(self):

		from ..essentials.all_connections import database_cursor
		self.db_obj_db_cms_fb = database_cursor('db_cms_fb','dev')

		query = "SELECT DISTINCT company_domain FROM `TBL_COMPANY_DOMAIN`"

		fetch_domains = self.db_obj_db_cms_fb.execute(query)

		fetch_domains = pd.DataFrame(list(fetch_domains))
		fetch_domains.columns = ['company_domain']

		fetch_domains['company_domain'] = fetch_domains['company_domain'].str.lower()

		print fetch_domains

		return fetch_domains

	def send_emails(self,df,admin_data,not_company_domain):
		import os
		import re

		current_dir = os.path.dirname(os.path.realpath(__file__))
		prefix = '/'.join(current_dir.split('/')[:current_dir.split('/').index('core')])
		postfix = '/core/essentials/email_template.txt'
		email_filename = prefix + postfix

		email_set = {}
		df = df.groupby(['email', 'name', 'role', 'tasks', 'type', 'type_id',
       'type_name']).sum()
		df = pd.DataFrame(df)
		df.drop(['id'],axis=1,inplace=True)

		data_out = df.to_html(escape=False)

		from ..essentials.mailer import MailGun
		with open(email_filename,'rb') as email_file:
			mailer_template = email_file.read()
		mailer_obj = MailGun()

		mailer_prefix = 'Kindly! Look at the table below for which access is still there but the email-id\'s are not present in our- Active Directory \r\n\r\n'
		body_iter = data_out

		if len(admin_data) > 3:
			mailer_prefix2 = '\n\nThere are more then 3 mail id\'s which have been given the Admin Rights please find the mail -id below \r\n\r\n'
			body_iter2 = admin_data

		mailer_prefix3 = '\n\nPlease Note that these Mail-id\'s are not there in our Dentsu Domain please have a review \r\n\r\n'
		body_iter3 = not_company_domain


		mailer_iter = re.split('{username}|{introduction}|{mail_body}',mailer_template)
		mailer_string = mailer_iter[0] + 'Team' + mailer_iter[1] + mailer_prefix + body_iter + '\n' + mailer_prefix2 + str(body_iter2) + '\n' + mailer_prefix3 + str(body_iter3) + mailer_iter[2]
				
		mailer_obj.send_email('info@dandatalab.com','nitesh.acharya@dentsuaegis.com',"DataLab: Update on Facebook- account access!",mailer_string,html=True)
		print mailer_obj

class FbAccountAccessCheckerMultipleAgency():
	
	def __init__(self):

		from ..essentials.all_connections import mongo
		import datetime

		from ..essentials.all_connections import database_cursor

		self.db_obj_accounts_tracker = database_cursor('accounts_tracker','production')
		self.db_obj_db_cms_fb = database_cursor('marketing_cloud','dmc')

		query = "SELECT distinct business_id,business_name FROM `fb_accounts_copy` "#WHERE report_status = 22"

		fetch_accounts = self.db_obj_accounts_tracker.execute(query)

		self.fetch_accounts_list = []

		for f_data in fetch_accounts:
			dct = {}
			dct['business_id'] = f_data[0]
			dct['business_name'] = f_data[1]
			self.fetch_accounts_list.append(dct)

		print self.fetch_accounts_list
		self.data_exception_list = []
		self.account_exception_list = []

		self.final_access_dump = pd.DataFrame()
		self.final_access_revoke_df = pd.DataFrame()
		self.final_admin_data = pd.DataFrame()
		self.final_not_company_domain = pd.DataFrame()


		# mongo_service = mongo('mongo_main')
		# mongo_client = mongo_service.get_client()
		# db = mongo_client["dandatalab"]
		# current_date = str(datetime.date.today()).split(' ')[0]
		# self.Table = db.get_collection("lasersight_output")

	def run(self):

		print "Total Count : " + str(len(self.fetch_accounts_list))
		i=1
		for business_data in self.fetch_accounts_list:
			i += 1
			print "current count : " + str(i)
			try:
				raw_fb_data = self.raw_fb_users_data(business_data['business_id'])
			except:
				pass
			try:
				raw_ad_data = self.raw_ad_data()
			except:
				pass
			try:
				raw_domain_data = self.raw_domain_data()
			except:
				pass

			try:
				raw_fb_data_main = raw_fb_data
				access_revoke_df = raw_fb_data[~raw_fb_data.email.isin(list(raw_ad_data['email']))]
				access_revoke_df.drop(['employee_name','company_domain'],axis=1,inplace=True)
				access_revoke_df['business_id'] = business_data['business_id']
				access_revoke_df['business_name'] = business_data['business_name']
				raw_fb_data_main['business_id'] = business_data['business_id']
				raw_fb_data_main['business_name'] = business_data['business_name']
				raw_fb_data_main = raw_fb_data_main.merge(raw_ad_data)
				self.final_access_revoke_df = self.final_access_revoke_df.append(access_revoke_df)
				self.final_access_dump = self.final_access_dump.append(raw_fb_data_main)
			except Exception as e:
				print "final raw data : error"
				print e
			
			try:
				admin_data = raw_fb_data[raw_fb_data['role']=='ADMIN']
				admin_data = list(admin_data['email'].unique())
				if len(admin_data) > 0 :
					admin_data = pd.DataFrame(admin_data)
					admin_data.columns = ["admin mail id's"]
					admin_data['business_id'] = business_data['business_id']
					admin_data['business_name'] = business_data['business_name']
					self.final_admin_data = self.final_admin_data.append(admin_data)
			except Exception as e:
				print "admin data : error"
				print e

			try:
				not_company_domain = raw_fb_data[~raw_fb_data.company_domain.isin(list(raw_domain_data['company_domain']))]
				not_company_domain = list(not_company_domain['email'].unique())
				not_company_domain = pd.DataFrame(not_company_domain)
				not_company_domain.columns = ["admin mail id's"]
				not_company_domain['business_id'] = business_data['business_id']
				not_company_domain['business_name'] = business_data['business_name']
				self.final_not_company_domain = self.final_not_company_domain.append(not_company_domain)
			except Exception as ex:
				print "not_company_domain : error"
				print ex
		
		#-------------------bulk insert master data -----------------------#
		self.final_access_dump = self.data_sorter(self.final_access_dump)
		if not self.final_access_dump.empty:
			self.final_access_dump = self.final_access_dump[['business_id','business_name','email','id','name','role','tasks','type','type_id','type_name','country']]
			self.final_access_dump.columns = ['business_id','business_name','email_id','user_id','name','role','tasks','type','type_id','type_name','country']
			access_revoke = [tuple(x) for x in self.final_access_dump.values]
		else:
			access_revoke = []
		
		mapper = {'column_array':
		['business_id','business_name','email_id','user_id','name','role','tasks','type','type_id','type_name','country'],
		'type_map':
		{'business_id':'str','business_name':'str','email_id':'str','user_id':'str','name':'str','role':'str','tasks':'str','type':'str','type_id':'str','type_name':'str','country':'str'}}
						
		insert_col_string = ','.join(mapper['column_array'])
		col_string = ','.join(["%s" if mapper['type_map'][col] == 'str' else "%s" for col in mapper['column_array']])
		if not self.final_access_dump.empty:
			totaldata = self.final_access_dump.to_records(index=False).tolist()
			delete_query = "Delete from fb_account_raw_data"
		else:
			totaldata = []

		query = "INSERT Into fb_account_raw_data ({insert_col_string}) VALUES ({value_string});".format(insert_col_string=insert_col_string,value_string=col_string)
		print query
		
		from ..essentials.all_connections import database_cursor

		self.db_obj = database_cursor('marketing_cloud','dmc')

		cursor = self.db_obj.get_cursor()
		if access_revoke:
			delete = cursor.execute(delete_query)
			data = cursor.executemany(query,access_revoke)
			self.db_obj.cxn.commit()
		self.db_obj.cxn.close()

		#-------------------bulk insert revoke accounts--------------------#
		self.final_access_revoke_df = self.data_sorter(self.final_access_revoke_df)
		
		if not self.final_access_revoke_df.empty:
			self.final_access_revoke_df = self.final_access_revoke_df[['business_id','business_name','email','id','name','role','tasks','type','type_id','type_name']]
			self.final_access_revoke_df.columns = ['business_id','business_name','email_id','user_id','name','role','tasks','type','type_id','type_name']
			access_revoke = [tuple(x) for x in self.final_access_revoke_df.values]
		else:
			access_revoke = []
		
		mapper = {'column_array':
		['business_id','business_name','email_id','user_id','name','role','tasks','type','type_id','type_name'],
		'type_map':
		{'business_id':'str','business_name':'str','email_id':'str','user_id':'str','name':'str','role':'str','tasks':'str','type':'str','type_id':'str','type_name':'str'}}
						
		insert_col_string = ','.join(mapper['column_array'])
		col_string = ','.join(["%s" if mapper['type_map'][col] == 'str' else "%s" for col in mapper['column_array']])
		if not self.final_access_revoke_df.empty:
			totaldata = self.final_access_revoke_df.to_records(index=False).tolist()
			delete_query = "Delete from fb_account_access_revoke"
		else:
			totaldata = []

		query = "INSERT Into fb_account_access_revoke ({insert_col_string}) VALUES ({value_string});".format(insert_col_string=insert_col_string,value_string=col_string)
		print query
		
		from ..essentials.all_connections import database_cursor

		self.db_obj = database_cursor('marketing_cloud','dmc')

		cursor = self.db_obj.get_cursor()
		if access_revoke:
			delete = cursor.execute(delete_query)
			data = cursor.executemany(query,access_revoke)
			self.db_obj.cxn.commit()
		self.db_obj.cxn.close()

		#----------------------- bulk insert admin data ----------------------------- 
		self.final_admin_data = self.data_sorter(self.final_admin_data)
		if not self.final_admin_data.empty:
			self.final_admin_data = self.final_admin_data[['business_id','business_name',"admin mail id's"]]
			self.final_admin_data.columns = ['business_id','business_name','email_id']
			admin_account_data = [tuple(x) for x in self.final_admin_data.values]
		else:
			admin_account_data = []
		
		mapper = {'column_array':
		['business_id','business_name','email_id'],
		'type_map':
		{'business_id':'str','business_name':'str','email_id':'str'}}
						
		insert_col_string = ','.join(mapper['column_array'])
		col_string = ','.join(["%s" if mapper['type_map'][col] == 'str' else "%s" for col in mapper['column_array']])
		if not self.final_admin_data.empty:
			totaldata = self.final_admin_data.to_records(index=False).tolist()
			delete_query = "Delete from fb_admin_account_data"
		else:
			totaldata = []

		query = "INSERT Into fb_admin_account_data ({insert_col_string}) VALUES ({value_string});".format(insert_col_string=insert_col_string,value_string=col_string)
		print query
		
		from ..essentials.all_connections import database_cursor

		self.db_obj = database_cursor('marketing_cloud','dmc')

		cursor = self.db_obj.get_cursor()
		if admin_account_data:
			delete = cursor.execute(delete_query)
			data = cursor.executemany(query,admin_account_data)
			self.db_obj.cxn.commit()
		self.db_obj.cxn.close()

		#-----------------------bulk insert different domain account data-------------------------
		self.final_not_company_domain = self.data_sorter(self.final_not_company_domain)
		if not self.final_not_company_domain.empty:
			self.final_not_company_domain = self.final_not_company_domain[['business_id','business_name',"admin mail id's"]]
			self.final_not_company_domain.columns = ['business_id','business_name','email_id']
			admin_account_data = [tuple(x) for x in self.final_not_company_domain.values]
		else:
			admin_account_data = []
		
		mapper = {'column_array':
		['business_id','business_name','email_id'],
		'type_map':
		{'business_id':'str','business_name':'str','email_id':'str'}}
						
		insert_col_string = ','.join(mapper['column_array'])
		col_string = ','.join(["%s" if mapper['type_map'][col] == 'str' else "%s" for col in mapper['column_array']])
		if not self.final_not_company_domain.empty:
			totaldata = self.final_not_company_domain.to_records(index=False).tolist()
			delete_query = "Delete from fb_account_different_domain"
		else:
			totaldata = []

		query = "INSERT Into fb_account_different_domain ({insert_col_string}) VALUES ({value_string});".format(insert_col_string=insert_col_string,value_string=col_string)
		print query
		
		from ..essentials.all_connections import database_cursor

		self.db_obj = database_cursor('marketing_cloud','dmc')

		cursor = self.db_obj.get_cursor()
		if admin_account_data:
			delete = cursor.execute(delete_query)
			data = cursor.executemany(query,admin_account_data)
			self.db_obj.cxn.commit()
		self.db_obj.cxn.close()
		#----------------------------------------------------------------------------------

		mail_shoot = self.send_emails(self.final_access_revoke_df,self.final_admin_data,self.final_not_company_domain)

		return self.final_access_revoke_df,self.final_admin_data,self.final_not_company_domain

	def raw_fb_users_data(self,buss_id):
		import time
		from facebook_business.api import FacebookAdsApi
		from facebook_business.adobjects.business import Business
		from ..essentials.all_connections import facebook_gautam
		from facebook_business.adobjects.adaccount import AdAccount

		token,version=facebook_gautam().main()

		FacebookAdsApi.init(access_token=token,api_version=version)

		buss_obj = Business(buss_id)
		buss_obj = buss_obj.get_business_users(fields={'id','role','name','email','assigned_ad_accounts','assigned_pages'},params={'limit':1})

		final_access_data = []
		
		for data in buss_obj:
			try:
				for assigned_ad_accounts_data in data['assigned_ad_accounts']['data']:
					try:
						dct = {}
						dct['tasks'] = assigned_ad_accounts_data['tasks']
						dct['type_id'] = assigned_ad_accounts_data['account_id']
						dct['type_name'] = ''
						dct['id'] = data['id']
						dct['name'] = data['name']
						dct['role'] = data['role']
						dct['email'] = data['email']
						dct['type'] = 'account'
						final_access_data.append(dct)
					except Exception as ex:
						print ex
			except Exception as ex:
				print ex

			try:
				for assigned_ad_accounts_data in data['assigned_pages']['data']:
					try:
						dct = {}
						dct['tasks'] = assigned_ad_accounts_data['tasks']
						dct['type_id'] = assigned_ad_accounts_data['id']
						dct['type_name'] = assigned_ad_accounts_data['name']
						dct['id'] = data['id']
						dct['name'] = data['name']
						dct['role'] = data['role']
						dct['email'] = data['email']
						dct['type'] = 'page'
						final_access_data.append(dct)
					except Exception as ex:
						print ex
			except Exception as ex:
				print ex
				
			try:
				dct = {}
				dct['id'] = data['id']
				try:
					dct['name'] = data['name']
				except:
					pass
				dct['role'] = data['role']
				dct['email'] = data['email']
				final_access_data.append(dct)
			except Exception as ex:
				print ex


		final_access_data.append({'email':'Gautam.Mehra@dentsuaegis.com','name':'Gautam Mehra','role':'ADMIN','id':data['id'],'name':data['name']})

		final_access_data_df = pd.DataFrame(final_access_data)

		final_access_data_df.fillna('na',inplace=True)
		final_access_data_df['email'] = final_access_data_df['email'].str.lower()
		final_access_data_df['tasks'] = final_access_data_df['tasks'].apply(lambda x : tuple(x) if type(x) is list else x)
		final_access_data_df['employee_name'],final_access_data_df['company_domain'] = zip(*final_access_data_df["email"].str.split('@').tolist())
		final_access_data_df.drop_duplicates(keep='first',inplace=True)

		account_id_list = {}
		account_list = list(final_access_data_df['type_id'].unique())
		for act_ in account_list:
		    data = AdAccount(str('act_')+str(act_))
		    try:
		        data_tp = data.api_get(fields={'name'})
		        account_id_list[act_]=data_tp['name']
		    except:
		        pass

		for i in range(1,len(final_access_data_df)):
		    if final_access_data_df.loc[i,'type'] == 'account':
		        final_access_data_df.loc[i,'type_name'] = account_id_list[final_access_data_df.loc[i,'type_id']]
		
		return final_access_data_df

	def raw_ad_data(self):

		from ..essentials.all_connections import database_cursor
		self.db_obj_db_cms_fb = database_cursor('marketing_cloud','dmc')

		query = "SELECT DISTINCT mail,country FROM `AD_Dump`"

		fetch_accounts = self.db_obj_db_cms_fb.execute(query)

		fetch_accounts = pd.DataFrame(list(fetch_accounts))
		fetch_accounts.columns = ['email','country']

		fetch_accounts['email'] = fetch_accounts['email'].str.lower()

		print fetch_accounts

		return fetch_accounts

	def raw_domain_data(self):

		from ..essentials.all_connections import database_cursor
		self.db_obj_db_cms_fb = database_cursor('marketing_cloud','dmc')

		query = "SELECT DISTINCT company_domain FROM `TBL_COMPANY_DOMAIN`"

		fetch_domains = self.db_obj_db_cms_fb.execute(query)

		fetch_domains = pd.DataFrame(list(fetch_domains))
		fetch_domains.columns = ['company_domain']

		fetch_domains['company_domain'] = fetch_domains['company_domain'].str.lower()

		print fetch_domains

		return fetch_domains

	def send_emails(self,df,admin_data,not_company_domain):
		import os
		import re

		current_dir = os.path.dirname(os.path.realpath(__file__))
		prefix = '/'.join(current_dir.split('/')[:current_dir.split('/').index('core')])
		postfix = '/core/essentials/email_template.txt'
		email_filename = prefix + postfix

		email_set = {}
		df = df.groupby(['business_id','business_name','email_id','user_id','name', 'role', 'tasks', 'type', 'type_id','type_name']).sum()
		#import pdb;pdb.set_trace()
		#df = pd.DataFrame(df['id'])
		df.reset_index(inplace=True)
		#data_out = df.to_html(escape=False)

		from ..essentials.mailer import MailGun
		with open(email_filename,'rb') as email_file:
			mailer_template = email_file.read()

		mailer_obj = MailGun()

		mailer_prefix = '1) Kindly! Find the attached file - "fb_access_checker_revoke_mail_id.csv" which contains mail-id which you need to lookon as they don\'t show up in our Active-Directory \r\n\r\n'
		#body_iter = data_out

		mailer_prefix2 = '\r\n\r\n2) Find the attached file - "fb_access_checker_admin_list.csv" if there are more then 3 Admin in Agency the mail-id\'s are listed here \r\n\r\n'
		# admin_data = admin_data.to_html(escape=False)
		# body_iter2 = admin_data

		mailer_prefix3 = '\r\n\r\n3) Find the attached file - "fb_access_checker_out_of_dan_domain.csv" which contains mail-id which are not in the Dentsu company domain list \r\n\r\n'
		# not_company_domain = not_company_domain.to_html(escape=False)
		# body_iter3 = not_company_domain


		mailer_iter = re.split('{username}|{introduction}|{mail_body}',mailer_template)
		mailer_string = mailer_iter[0] + 'Team' + mailer_iter[1] + mailer_prefix + '\r\n\r\n' + mailer_prefix2 + '\r\n\r\n' + mailer_prefix3 + mailer_iter[2]

		tempdf1 = []
		for i, r in df.iterrows():
		    row_dict = {}
		    colnames = list(r.index)
		    val = r.tolist()
		    for val in colnames:
		        try:
		            valstr = str(r[val]).encode('utf-8')
		            row_dict[val] = valstr
		        except:
		            test_str = ''
		            for char in r[val]:
		                try:
		                    words = str(char).encode('utf-8')
		                    test_str = test_str + words
		                except:
		                    test_str = test_str + ' '
		            row_dict[val] = test_str

		    tempdf1.append(row_dict)

		df = pd.DataFrame(tempdf1)

		tempdf1 = []
		for i, r in admin_data.iterrows():
		    row_dict = {}
		    colnames = list(r.index)
		    val = r.tolist()
		    for val in colnames:
		        try:
		            valstr = str(r[val]).encode('utf-8')
		            row_dict[val] = valstr
		        except:
		            test_str = ''
		            for char in r[val]:
		                try:
		                    words = str(char).encode('utf-8')
		                    test_str = test_str + words
		                except:
		                    test_str = test_str + ' '
		            row_dict[val] = test_str

		    tempdf1.append(row_dict)

		admin_data = pd.DataFrame(tempdf1)

		tempdf1 = []
		for i, r in not_company_domain.iterrows():
		    row_dict = {}
		    colnames = list(r.index)
		    val = r.tolist()
		    for val in colnames:
		        try:
		            valstr = str(r[val]).encode('utf-8')
		            row_dict[val] = valstr
		        except:
		            test_str = ''
		            for char in r[val]:
		                try:
		                    words = str(char).encode('utf-8')
		                    test_str = test_str + words
		                except:
		                    test_str = test_str + ' '
		            row_dict[val] = test_str

		    tempdf1.append(row_dict)

		not_company_domain = pd.DataFrame(tempdf1)

		df.to_csv('/var/python/core-prasad/corepython/core/src/fb_access_checker_revoke_mail_id.csv')
		admin_data.to_csv('/var/python/core-prasad/corepython/core/src/fb_access_checker_admin_list.csv')
		not_company_domain.to_csv('/var/python/core-prasad/corepython/core/src/fb_access_checker_out_of_dan_domain.csv')
				
		mailer_obj.send_email('info@dandatalab.com','nitesh.acharya@dentsuaegis.com',"DataLab: Update on Facebook- account access!",mailer_string,[('attachment',open('/var/python/core-prasad/corepython/core/src/fb_access_checker_revoke_mail_id.csv')),
			('attachment',open('/var/python/core-prasad/corepython/core/src/fb_access_checker_admin_list.csv')),
			('attachment',open('/var/python/core-prasad/corepython/core/src/fb_access_checker_out_of_dan_domain.csv'))],html=True)
		print mailer_obj

	def data_sorter(self,df):
		import pandas as pd
		tempdf1 = []
		for i, r in df.iterrows():
		    row_dict = {}
		    colnames = list(r.index)
		    val = r.tolist()
		    for val in colnames:
		        try:
		            valstr = str(r[val]).decode('ascii')
		            row_dict[val] = valstr
		        except:
		            test_str = ''
		            for char in r[val]:
		                try:
		                    words = str(char).decode('ascii')
		                    test_str = test_str + words
		                except:
		                    test_str = test_str + ' '
		            row_dict[val] = test_str

		    tempdf1.append(row_dict)

		df = pd.DataFrame(tempdf1)

		return df

class FbAccountAccessibleRetrieve():
	
	def __init__(self,):

		from ..essentials.all_connections import mongo
		import datetime

		from ..essentials.all_connections import database_cursor

		self.db_obj_accounts_tracker = database_cursor('accounts_tracker','production')
		self.db_obj_db_cms_fb = database_cursor('marketing_cloud','dmc')

	def run(self,emp_id,business_id,get_info,delete_info):

		print emp_id
		print business_id
		if get_info == 1:
			business_list = self.get_access_info(emp_id)
			return business_list

		if delete_info == 1:
			business_list = self.get_delete_info(emp_id,business_id)
			return business_list
		
		try:
			raw_access_revoke_data = self.get_access_revoke_data(emp_id,business_id)
		except Exception as E:
			print E
			raw_access_revoke_data = []

		try:
			raw_admin_account_data = self.get_admin_account_data(business_id)
		except Exception as E:
			print E
			raw_admin_account_data = []

		try:
			raw_different_domain_account = self.get_different_domain_account(business_id)
		except Exception as E:
			print E
			raw_different_domain_account = []

		try:
			raw_flagged_admin_data = self.get_flagged_admin_data(business_id)
		except Exception as E:
			print E
			raw_flagged_admin_data = []	
		
		data = {'access_revoke_data':raw_access_revoke_data,'admin_account_data':raw_admin_account_data,'different_domain_account':raw_different_domain_account,'flagged_admin_data':raw_flagged_admin_data}
		return data

	def get_access_info(self,emp_id):
		
		query_type_id = "SELECT DISTINCT business_id,business_name FROM fb_account_raw_data WHERE email_id='{emp_id}'".format(emp_id=emp_id)
		print query_type_id
	
		records_type_id = self.db_obj_db_cms_fb.execute(query_type_id)

		business_list=[]

		for val in records_type_id:
			dct = {}
			dct['business_id'] = int(val[0])
			dct['business_name'] = str(val[1])
			business_list.append(dct)

		print business_list

		return business_list

	def get_delete_info(self,emp_id,business_id):
		
		query_type_id = "Delete FROM fb_account_access_revoke WHERE user_id={user_id} and business_id = {business_id}".format(emp_id=emp_id,business_id=business_id)
		print query_type_id
	
		records_type_id = self.db_obj_db_cms_fb.execute(query_type_id)

		business_list = True

		return business_list

	def get_access_revoke_data(self,emp_id,business_id):
		
		query_type_id = "SELECT DISTINCT(type_id) FROM fb_account_raw_data WHERE role='ADMIN' AND email_id='{emp_id}'".format(emp_id=emp_id)
		print query_type_id
	
		records_type_id = self.db_obj_db_cms_fb.execute(query_type_id)

		access_revoke_list = []
		type_id_list = []

		for val in records_type_id:
			type_id_list.append(str(val[0]))

		print type_id_list

		query = "SELECT distinct * FROM fb_account_access_revoke WHERE role='ADMIN' AND type_id in {type_id} AND email_id NOT IN (SELECT email_id FROM fb_account_different_domain WHERE business_id={business_id}) and business_id = {business_id}".format(type_id=type_id_list,business_id=business_id)
		query = query.replace('[','(')
		query = query.replace(']',')')
		print query
		records = self.db_obj_db_cms_fb.execute(query)
		
		for val in records:
			dct={}
			dct['business_id']=val[1]
			dct['business_name']=val[2]
			dct['email_id']=val[3]
			dct['user_id']=val[4]
			dct['name']=val[5]
			dct['role']=val[6]
			dct['tasks']=val[7]
			dct['type']=val[8]
			dct['type_id']=val[9]
			dct['type_name']=val[10]
			access_revoke_list.append(dct)

		print access_revoke_list

		return access_revoke_list

	def get_admin_account_data(self,business_id):
		
		query = "SELECT distinct main.email_id,main.business_id,main.business_name,sub.type,sub.type_name FROM fb_admin_account_data as main left join fb_account_raw_data as sub on main.email_id = sub.email_id WHERE main.business_id={business_id} and main.email_id not in ('gautam.mehra@dentsuaegis.com','abhinay.bhasin@dentsuaegis.com','nishant.malsisaria@webchutney.net','gautam.mehra@iprospect.com')".format(business_id=business_id)
		print query
		
		records = self.db_obj_db_cms_fb.execute(query)

		admin_account_list = []

		for val in records:
			dct={}
			dct['email_id']=val[0]
			dct['business_id']=val[1]
			dct['business_name']=val[2]
			dct['type']=val[3]
			dct['type_name']=val[4]
			
			admin_account_list.append(dct)

		print admin_account_list

		return admin_account_list	
		
	def get_different_domain_account(self,business_id):
		
		query = "SELECT distinct main.email_id,main.business_id,main.business_name,sub.type,sub.type_name FROM fb_account_different_domain as main left join fb_account_raw_data as sub on main.email_id = sub.email_id WHERE main.business_id={business_id}".format(business_id=business_id)
		print query
		
		records = self.db_obj_db_cms_fb.execute(query)

		different_domain_account_list = []

		for val in records:
			dct={}
			dct['email_id']=val[0]
			dct['business_id']=val[1]
			dct['business_name']=val[2]
			dct['type']=val[3]
			dct['type_name']=val[4]
			
			different_domain_account_list.append(dct)

		print different_domain_account_list

		return different_domain_account_list		

	def get_flagged_admin_data(self,business_id):
		query = "SELECT distinct sub.type_id,sub.type_name FROM fb_admin_account_data as main left join fb_account_raw_data as sub on main.email_id = sub.email_id WHERE main.business_id={business_id} AND sub.type_id is NOT NULL and main.email_id not in ('gautam.mehra@dentsuaegis.com','abhinay.bhasin@dentsuaegis.com','nishant.malsisaria@webchutney.net','gautam.mehra@iprospect.com') GROUP BY sub.type_id HAVING COUNT(DISTINCT(main.email_id))>=3".format(business_id=business_id)
		print query
		
		records = self.db_obj_db_cms_fb.execute(query)

		admin_account_list = []

		for val in records:
			dct={}
			dct['type_id']=val[0]
			dct['type_name']=val[1]
			#dct['business_name']=val[2]
			#dct['type']=val[3]
			#dct['type_name']=val[4]
			
			admin_account_list.append(dct)

		print admin_account_list

		flagged_admin_data = []

		flagged_account_data = {}
		
		flagged_account_data['flagged_account_data'] = admin_account_list

		flagged_admin_data.append(flagged_account_data)
		
		flagged_account_count = {}

		flagged_account_count['flagged_account_count'] = len(admin_account_list)

		flagged_admin_data.append(flagged_account_count)
		
		query_total_account = "SELECT COUNT(DISTINCT(type_id)) as total_records FROM `fb_account_raw_data` WHERE type_id is NOT NULL AND type_name is NOT NULL"
		print query
		
		records_total_account = self.db_obj_db_cms_fb.execute(query_total_account)

		total_records = []

		for val in records_total_account:
			dct={}
			dct['total_records']=val[0]
			
			flagged_admin_data.append(dct)

		#flagged_admin_data.append(total_records)

		return flagged_admin_data

if __name__ == '__main__':
	buss_id = ['987483671331612']
	#obj = FbAccountAccessCheckerMultipleAgency().run()
	#obj = FbAccountAccessibleRetrieve().get_access_revoke_data('sanjishilizi@gmail.com')
	obj = FbAccountAccessibleRetrieve().run(emp_id='iprospectsmbfb@gmail.com',business_id='987483671331612',get_info=False)