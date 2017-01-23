import requests
import click
from lxml import html
from terminaltables import AsciiTable
import re


def get_fixture():
    page = requests.get("http://www.tff.org/default.aspx?pageID=198")
    tree = html.fromstring(page.content)
    global fixture_weeks
    fixture_weeks = tree.xpath('//table[@class="softBG"]')
    global current_week
    current_week = tree.get_element_by_id('ctl00_MPane_m_198_935_ctnr_m_198_935_hs_Tab2').findall('span')[0].text_content().split('.')[0]
    current_week = int(current_week)

def get_table():
    page = requests.get("http://www.sporx.com/futbol-super-lig")
    tree = html.fromstring(page.content)
    table = tree.xpath('//ul[@class="pdlist"]/li')
    click.secho("\nPUAN DURUMU", fg='red', bg='yellow', bold=True, blink=True)
    table_data = []
    for row in table:
        row_text = row.text_content()
        row_text = re.sub(r'[\t\r]+', '', row_text)
        row_text = row_text.split('\n')
        table_data.append(row_text[1:11])
    table = AsciiTable(table_data)
    print(table.table)

def show_week(week):
    week_games = fixture_weeks[week-1].findall('tr')[1].text_content().split('\r\n\t\t\t\t\t\t\r\n\t\t\t\t\t\t\r\n\t\t\t\t\t\t\t')
    str = "Spor Toto Süper Lig %d. Hafta Maçları" % week
    click.secho(str, fg='red', bg='yellow', bold=True, blink=True)
    for game in week_games:
        str = re.sub(r'[\r\n\t]+',' ', game)
        str = str.lstrip(' ')
        print(str)

@click.command()
@click.option('--hafta', default=18, help="İstediğiniz haftanın maçlarını gösterir.")
def main(hafta):
    """Spor Toto Süper Lig hakkında bilgiler alabileceğiniz, komut satırı üzerinden çalışan program."""
    get_fixture()
    show_week(hafta)
    get_table()

if __name__ == '__main__':
    main()
