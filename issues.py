import requests

issues = []
per_page = 100

def get_page(page, per_page):
    response = requests.get(f"https://api.github.com/repos/Eggs-D-Studios/wos-issues/issues?page={page}&per_page={per_page}&direction=asc")
    return response.json()

page_index = 0

def get_all_new_issues():
    global page_index
    while True:
        page = get_page(page_index, per_page)
        for issue in page:
            index = issue['number']-1
            if index < len(issues):
                issues[index] = issue
            else:
                issues.append(issue)
        if len(page) < per_page:
            break
        page_index += 1

    print(f"There are now {len(issues)} issues")
    return issues