import requests
import json

class GetLibs():
	def __init__(self):
		self.git = json.load(open('git.json', 'r'))

	def get_pjts(self):
		all_pjts = []
		count = 0

		while True:
			count +=1
			api_git = f"{self.git['url']}/api/v4/projects?page={count}"
			request = requests.get(api_git, headers=self.git['header'], verify=False)
			result = request.json()
			if len(result) == 0: break

			[all_pjts.append(i['id']) for i in result]
		
		return all_pjts

	def search_libs(self, pjts):
		count = 0
		total = len(pjts)
		
		all_libs = []
		lib_url = 'https://pypi.org/pypi'

		for pjt_id in pjts:
			count += 1
			print(f"status: {count}/{total}")

			api_git = f"{self.git['url']}/api/v4/projects/{pjt_id}/repository/tree"
			request = requests.get(api_git, headers=self.git['header'], verify=False)
			if request.status_code != 200: continue
			
			result = request.json()
			if len(result) == 0: continue

			py_files = [i['name'] for i in result if i['name'].endswith('.py')]
			if len(py_files) == 0: continue	

			for p in py_files:
				api_git = f"{self.git['url']}/api/v4/projects/{pjt_id}/repository/files/{p}/raw"
				request = requests.get(api_git, headers=self.git['header'], verify=False)
				libs_1 = [i.split('from ')[1].split(' ')[0].split('.')[0].strip() for i in request.text.split('\n') if i.startswith('from ')]
				libs_2 = [i.split('import ')[1].split(' ')[0].strip() for i in request.text.split('\n') if i.startswith('import ')]
				
				full_libs = list(set(libs_1 + libs_2))			
				[all_libs.append(i) for i in full_libs if requests.get(f"{lib_url}/{i}/json", timeout=3).status_code == 200 and i not in all_libs]
		
		return all_libs
	
	def main(self):
		all_pjts = self.get_pjts()			
		all_libs = self.search_libs(all_pjts)
		return all_libs
	
if __name__ == '__main__':
	run = GetLibs()
	result = run.main()
	open('requirements.txt', 'w').write('\n'.join(result))

