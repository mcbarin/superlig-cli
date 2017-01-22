import requests
import click
from lxml import html
import re


def get_fixture():
    page = requests.get("http://www.tff.org/default.aspx?pageID=198")
    tree = html.fromstring(page.content)
    global fixture_weeks
    fixture_weeks = tree.xpath('//table[@class="softBG"]')
    global current_week
    current_week = tree.get_element_by_id('ctl00_MPane_m_198_935_ctnr_m_198_935_hs_Tab2').findall('span')[0].text_content().split('.')[0]
    current_week = int(current_week)

def show_week(week):
    week_games = fixture_weeks[week-1].findall('tr')[1].text_content().split('\r\n\t\t\t\t\t\t\r\n\t\t\t\t\t\t\r\n\t\t\t\t\t\t\t')
    for game in week_games:
        print(re.sub(r'[\r\n\t]+',' ', game))

@click.command()
@click.option('--hafta', default=18, help="İstediğiniz haftanın maçlarını gösterir.")
def main(hafta):
    get_fixture()
    show_week(hafta)

if __name__ == '__main__':
    main()
