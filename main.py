from typing import List

import datetime

from utils import get_game_pages, GamePage


class Round(object):
    round_no: int
    player: str
    name: str
    category: str
    name_another: str
    challenged: bool
    game: GamePage
    played: datetime

    def __init__(self, row_str: str, game: GamePage, played: datetime):
        entries = row_str.replace('</td><td>', '\n').replace('<td>', '').replace('</td>', '').split('\n')
        self.round_no = int(entries[0])
        self.player = entries[1]
        self.name = self.convert_name(entries[2])
        self.category = entries[3]
        self.name_another = entries[4]
        self.game = game
        self.challenged = "✔" in entries[5]
        self.played = played

    def convert_name(self, name_html_str: str) -> str:
        return name_html_str.replace('<a target="_blank" rel="nofollow noreferrer noopener" class="external text" href="', '[')\
            .replace('">', ' ').replace('</a>', ']')

    def get_play_summary(self) -> str:
        starting_str = f'{self.player}: {self.game.as_wiki_link()}'
        if self.challenged:
            starting_str += ' ✘'
        return starting_str

    def __str__(self):
        return f'#{self.round_no} - {self.player}: {self.name}'


def parse_plays(game_page: GamePage, player_to_plays: dict[str, List[Round]]):
    rows = game_page.raw_plays_table.replace('</tr><tr>', '\n').replace('<tr>', '').replace('</tr>', '').split('\n')
    rows.pop(0)
    parsed_rounds = [Round(row, game_page, game_page.recorded_date) for row in rows]
    for round in parsed_rounds:
        existing_list = player_to_plays.get(round.name, [])
        existing_list.append(round)
        existing_list = sorted(existing_list, key=lambda item: item.played)
        player_to_plays[round.name] = existing_list


def get_play_summary(plays: List[Round]) -> str:
    return '\n\n'.join([play.get_play_summary() for play in plays])


def get_first_named(plays: List[Round]) -> str:
    plays_by_date = sorted(plays, key=lambda round: round.played)[0]
    return plays_by_date.played.strftime("%Y-%m-%d")


if __name__ == '__main__':
    pages = get_game_pages()

    player_to_plays: dict[str, List[Round]] = {}

    for page in pages:
        parse_plays(page, player_to_plays)

    sorted_plays = dict(sorted(player_to_plays.items(), key=lambda item: -len(item[1])))

    results_table_str = '{| class="article-table sortable"\n|+All Names\n!Name\n!Count\n!First named\n!Games\n'

    for item in sorted_plays.items():
        name = item[0]
        count = len(item[1])
        first_named = get_first_named(item[1])
        plays = get_play_summary(item[1])
        results_table_str += f'|-\n|{name}\n|{count}\n|{first_named}\n|{plays}\n'

    results_table_str += '|}'

    page_source_str = f'This table has been [https://github.com/alexburlton/jockey-scraper auto-generated] by scraping {len(pages)} ' \
                      f'[[:Category:Game|game pages]] from this wiki - please do not edit it manually. The page can be ' \
                      f'regenerated by running the code again as more games are added.\n<br /><br />' \
                      f'\nIn total, \'\'\'{len(sorted_plays)} unique people\'\'\' have been named.\n<br />\n' \
                      f'If you like seeing stats like these, be sure to check out https://nomorepeoplewevehadbefore.co.uk/, which has a bunch more!' \
                      f'<br />\n {results_table_str}'

    print(page_source_str)
