import re
from dataclasses import dataclass
from datetime import datetime

from application.common.client import AsyncAppClient
from application.common.parser import Parser
from domain.common.news import News


@dataclass
class GetNews:
    parser: Parser
    async_client: AsyncAppClient

    async def __call__(self) -> list[News]:
        date = datetime.now()
        day = date.day
        month = date.month
        year = date.year
        link = "https://dvinanews.ru/calendar/?month={0}&year={1}&day={2}&start={2}.{0}.{1}&stop={2}.{0}.{1}".format(
            month, year, day
        )
        result = []
        async with self.async_client.get(link) as response:
            if response.status == 200:
                self.parser.__init__(await response.text(), "html.parser")
                all_news = self.parser.find("div", {"class": "calendarNews"})
                all_news = all_news.find_all("div", {"class": "col-8"})

                for news in all_news:
                    link = "https://dvinanews.ru" + news.find("a")["href"]
                    posted_at = f"{day}/{month}/{year} {news.find("span").text}"
                    date_format = "%d/%m/%Y %H:%M"
                    posted_at = datetime.strptime(posted_at, date_format)
                    text = news.find("div", {"class": "calendarNewsText"}).text.strip()
                    clean_text = re.sub("^\d{1,2}:\d{2}", "", text)

                    news = News(
                        link=link,
                        posted_at=posted_at,
                        title=clean_text,
                    )
                    result.append(news)
                if len(result) > 10:
                    result = result[:10]
            else:
                return []

        return result
