import flet as ft
import requests
import configparser
import webbrowser
import re
import pyperclip
import sys

#sets up the config file reader
config = configparser.ConfigParser()

#sets the config file name
configFile = "config.ini"

#reads the config file
config.read(configFile)

#only run first time setup if config file is empty
if config.sections() == []:

  #stores the new config in a tempory config file
  new_config = configparser.ConfigParser()
  
  #start first time setup
  def main(page: ft.Page):
    page.title = "AnonAddy Send From Alias - Setup"
    page.window_height = 470
    page.window_width = 700
    page.window_resizable = False
    
    
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    
    #shortcut to open anonaddy settings page
    def get_token(e):
      webbrowser.open("https://app.anonaddy.com/settings")

    #stores the token in the config file
    def tokenStore(e):
      if token_input.value != "" and len(token_input.value) == 40:
        new_config["API_Token"] = {'Token':token_input.value}
        token_input.error_text = ""
        page.update()
      else:
        token_input.error_text = "Please enter a valid token"
        page.update()

    #stores the sort order in the config file
    def sortStore(e):
      if sort_input.value != None:
        new_config["API_Sort"] = {'Sort':sort_input.value}
        sort_input.error_text = ""
        page.update()
      else:
        sort_input.error_text = "Please enter a valid sort order"
        page.update()

    #checks if the token is valid
    def verifyAPI(e):
      try:
        token = new_config["API_Token"]["Token"]
      except KeyError:
        key_check_status.value = "Please enter a API token before verifying"
        page.update()
        return

      headers = {
  'Content-Type': 'application/json',
  'X-Requested-With': 'XMLHttpRequest',
  'Authorization': 'Bearer ' + new_config["API_Token"]["Token"]
  }
      #INSERT MESSAGE TO SAY THAT THE CHECK IS STARTING
      key_check_status.value = "Verifying API token..."
      page.update()
      verify_api_response = requests.request('GET', "https://app.anonaddy.com/api/v1/api-token-details", headers=headers)
      if str(verify_api_response) == "<Response [200]>":
        key_check_status.value = "API token verified ✅"
        page.update()
      else:
        key_check_status.value = "API token invalid ❌"
        page.update()

    def save(e):
        with open(configFile, 'w') as configfile:
          new_config.write(configfile)
        page.clean()
        setup_complete_heading = ft.Text("Setup complete!", size=80, weight="BOLD", color="#8eb5e4", font_family="sans-serif", text_align="CENTER")
        close_window_prompt = ft.Text("You can now close this window", size=40, color="#8eb5e4", font_family="sans-serif", text_align="CENTER")
        setup_complete = ft.Column(spacing=10, controls=[setup_complete_heading, close_window_prompt])
        page.add(setup_complete)
        page.update() 
  
    #if the user wishes to have a default alias, this function will get all the aliases and add them to a dropdown so the user can pick one
    def get_defult_alias(e):
      def store_defult_alias(e):
        new_config["Default_Alias"] = {'Alias':defult_alias_dropdown.value}
        save(e)
      page.clean()
      header_select_alias = ft.Text("Select a default alias", size=40, weight="BOLD" ,color="#8eb5e4", font_family="sans-serif")
      sub_header_select_alias = ft.Text("This will be the alias that is automatically used if no other alias is selected", size=20, color="#8eb5e4", font_family="sans-serif")
      params = {
        'filter[active]': 'true',
        'sort': new_config["API_Sort"]["sort"],
      }
      headers = {
        'Content-Type': 'application/json',
        'X-Requested-With': 'XMLHttpRequest',
        'Authorization': 'Bearer ' + new_config["API_Token"]["token"]
      }
      response = requests.request('GET', 'https://app.anonaddy.com/api/v1/aliases', headers=headers, params=params).json()
      response = response["data"]


      list_of_aliases = []
      for alias in response:
          list_of_aliases.append(ft.dropdown.Option(alias["email"]))
      defult_alias_dropdown = ft.Dropdown(label="Pick a default alias", options=list_of_aliases)
      submit_defult_alias = ft.ElevatedButton("Save", on_click=store_defult_alias)
      page.add(header_select_alias, sub_header_select_alias, defult_alias_dropdown, submit_defult_alias)
      page.update()
      return
      
   
        
    def submit(e):
      if key_check_status.value == "API token verified ✅" and sort_input.value != None:
        if pick_defult_alias.value == True: #if the user wants a default alias, get the default alias then save the config
          get_defult_alias(e)
        else:
          save(e)

    


        
    headText = ft.Text("AnonAddy Send From Alias first time setup", size=30, color="#8eb5e4", font_family="sans-serif")
    header_divider = ft.Divider(thickness=3)
    
    token_input = ft.TextField(label="Token from AnonAddy", border_color="#43474e", focused_border_color="#9ecaff", on_change=tokenStore, width=530)
    verify_btn = ft.ElevatedButton(text="Verify", on_click=verifyAPI)
    get_token_button = ft.ElevatedButton(text="Get API token", on_click=get_token)
    
    key_check_status = ft.Text(value="Not yet Verified API token", size=20, color="Grey")
    input_row = ft.Row(spacing = 10, controls = [token_input, get_token_button])
    verify_row = ft.Row(spacing = 10, controls = [verify_btn, key_check_status])
    divider = ft.Divider(thickness=3)
    
    sort_input = ft.Dropdown(label="Sort aliases by", options=[ft.dropdown.Option("local_part"),
                                                       ft.dropdown.Option("domain"),
                                                       ft.dropdown.Option("email"),
                                                       ft.dropdown.Option("emails_forwarded"),
                                                       ft.dropdown.Option("emails_replied"),
                                                       ft.dropdown.Option("emails_sent"),
                                                       ft.dropdown.Option("created_at"),
                                                       ft.dropdown.Option("updated_at"),
                                                       ft.dropdown.Option("emails_blocked"),
                                                       ft.dropdown.Option("active")],
                             border_color="#43474e", focused_border_color="#9ecaff", helper_text="This determines order that the aliases will appear in the app's dropdown",
                             on_change=sortStore, width=690)
    submit_divider = ft.Divider(thickness=3)
    submit_button = ft.FilledButton(text="Submit", width=500, on_click=submit)
    pick_defult_alias = ft.Checkbox(label="Pick default alias", value=True)
    submit_row = ft.Row(spacing = 10, controls =[submit_button, pick_defult_alias])
    
    page.add(headText, header_divider, input_row, verify_row, divider, sort_input, submit_divider, submit_row)
  ft.app(target=main)
  sys.exit()




params = {
  'filter[active]': 'true',
  'sort': config["API_Sort"]["sort"],
}
headers = {
  'Content-Type': 'application/json',
  'X-Requested-With': 'XMLHttpRequest',
  'Authorization': 'Bearer ' + config["API_Token"]["token"]
}
response = requests.request('GET', 'https://app.anonaddy.com/api/v1/aliases', headers=headers, params=params).json()
try:
  response = response["data"]
except KeyError:
  with open("config.ini", "r+") as f:
    f.truncate(0)
  raise Exception("API token is invalid, the config has been deleted, please restart the app")

list_of_aliases = []
for alias in response:
    list_of_aliases.append(ft.dropdown.Option(alias["email"]))



def main(page: ft.Page):
    page.title = "AnonAddy Send From Alias"
    page.window_height = 380
    page.window_width = 500
    page.window_resizable = False
    page.window_maximizable = False
    
    
    
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    
    headtext = ft.Text("AnonAddy Send From Alias", size=30, color="#8eb5e4", font_family="sans-serif", weight="BOLD", text_align="CENTER")
    header_divider = ft.Divider(thickness=5)
    
    def use_default_alias_clicked(e):
      if use_default_alias.value == True and alias_options.value != None:
        alias_options.value = config["Default_Alias"]["alias"]
        page.update()
    
    def alias_dropdown_clicked(e):
      try:
        if use_default_alias.value == True:
          use_default_alias.value = False
          page.update()
      except:
        pass
        #user must not have set a default alias
    
    def check_real_email(email):
      regex_to_check_email = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
      if re.fullmatch(regex_to_check_email, email):
        return True
      else:
        return False
    
    def check_input_address_is_real_email(e):
      if check_real_email(input_address.value) == False:
        input_address.error_text = "Not a valid email address"
        page.update()
      else:
        input_address.error_text = ""
        page.update()
    
    input_address = ft.TextField(label="Input address", border_color="#43474e", focused_border_color="#9ecaff", width=450, on_change=check_input_address_is_real_email)
    adress_from_clipboard = pyperclip.paste() 
    if check_real_email(adress_from_clipboard):
      input_address.value = adress_from_clipboard
      page.update()
    
    def alias_adress_converter():
      #lol this one function is the whole purpose of this app
      adress_to_send_to = input_address.value
      adress_to_send_from = alias_options.value
      
      left_part = adress_to_send_from.split("@")[0]
      right_part = adress_to_send_from.split("@")[1]
      
      adress_to_send_to = adress_to_send_to.replace("@", "=")
      
      return f"{left_part}+{adress_to_send_to}@{right_part}"
    
    def show_converted_adress(e):
      converted_adress = alias_adress_converter()
      pyperclip.copy(converted_adress)
      page.clean()
      
      output_headtext = ft.Text("Your converted adress", size=30, color="#8eb5e4", font_family="sans-serif", weight="BOLD", text_align="CENTER")
      output_divider = ft.Divider(thickness=5)
      output_email = ft.TextField(value=converted_adress, border_color="#43474e", focused_border_color="#9ecaff", width=500, read_only=True)
      small_text = ft.Text("This adress has been copied to your clipboard", size=10, color="#8eb5e4", font_family="sans-serif", weight="BOLD", text_align="CENTER")
      page.add(output_headtext, output_divider, output_email, output_divider, small_text)
      page.update()
      
    alias_options = ft.Dropdown(width=450, options=list_of_aliases, label="Pick an alias",
                                border_color="#43474e", focused_border_color="#9ecaff", on_change=alias_dropdown_clicked)
    
    submit_btn = ft.ElevatedButton(text="Get adress", on_click=show_converted_adress, width=200)
    vertical_divider = ft.VerticalDivider(width=9, thickness=3, color="#43474e")
    
    try :
      alias_options.value = config["Default_Alias"]["alias"]
      page.update()
      use_default_alias = ft.Switch(label="Use default alias  ", label_position="LEFT", value=True, on_change=use_default_alias_clicked)
      submit_row = ft.Row(spacing = 10, controls=[submit_btn, vertical_divider, use_default_alias], alignment=ft.MainAxisAlignment.CENTER)
    except KeyError:
      submit_row = ft.Row(spacing = 10, controls=[submit_btn], alignment=ft.MainAxisAlignment.CENTER)
   
    def delete_config(e):
      with open("config.ini", "r+") as f:
        f.truncate(0)
      page.clean()
      page.add(headtext, header_divider, ft.Text("Config deleted", size=30, color="#EF5350", font_family="sans-serif", weight="BOLD", text_align="CENTER"))
      page.update()
   
    delete_config_btn = ft.ElevatedButton(text="Delete config", color="#EF5350", on_click=delete_config, width=200)
    
    page.add(headtext, header_divider, input_address, alias_options, submit_row, delete_config_btn)

ft.app(target=main)