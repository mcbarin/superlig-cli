import requests
import click
from lxml import html
from terminaltables import AsciiTable
import re

def get_fixture():
    page = requests.get("http://www.tff.org/default.aspx?pageID=198")
    global tree
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
    print()
    click.secho("PUAN DURUMU", fg='red', bg='yellow', bold=True, blink=True)
    table_data = []
    for row in table:
        row_text = row.text_content()
        row_text = re.sub(r'[\t\r]+', '', row_text)
        row_text = row_text.split('\n')
        table_data.append(row_text[1:11])
    table = AsciiTable(table_data)
    print(table.table)

def show_week(week):
    str = "Spor Toto Süper Lig %d. Hafta Maçları" % week
    click.secho(str, fg='red', bg='yellow', bold=True, blink=True)
    if week==current_week:
        detailed_week = tree.xpath('//table[@id="ctl00_MPane_m_198_935_ctnr_m_198_935_dtlHaftaninMaclari"]/tr/td//span')
        detailed_data = []
        detailed_data.append(["Tarih", "Ev Sahibi", "Skor", "Deplasman"])
        for index in range(0,9):
            temp_index = index*7
            date = "%s %s" % (detailed_week[temp_index].text_content(), detailed_week[temp_index+1].text_content())
            home = detailed_week[temp_index+2].text_content()
            score = "%s-%s" % (detailed_week[temp_index+3].text_content(), detailed_week[temp_index+4].text_content())
            away = detailed_week[temp_index+5].text_content()
            detailed_data.append([date, home, score, away])
        table = AsciiTable(detailed_data)
        print(table.table)
    else:   
        week_games = fixture_weeks[week-1].findall('tr')[1].text_content().split('\r\n\t\t\t\t\t\t\r\n\t\t\t\t\t\t\r\n\t\t\t\t\t\t\t')
        for game in week_games:
            str = re.sub(r'[\r\n\t]+',' ', game)
            str = str.lstrip(' ')
            print(str)

get_fixture()
@click.command()
@click.option('--week', default=current_week, help="İstediğiniz haftanın maçlarını gösterir.")
def main(week):
    """Spor Toto Süper Lig hakkında bilgiler alabileceğiniz, komut satırı üzerinden çalışan program."""
    show_week(week)
    get_table()

if __name__ == '__main__':
    main()
