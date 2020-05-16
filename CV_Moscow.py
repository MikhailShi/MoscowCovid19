#!bash python=3.6

# To analyze data of deaths in Moscow
# https://data.mos.ru/opendata/7704111479-dinamika-registratsii-aktov-grajdanskogo-sostoyaniya?pageNumber=13&versionNumber=3&releaseNumber=42

import io
import requests
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import date, datetime, timedelta
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()


zip_file_url = "https://op.mos.ru/EHDWSREST/catalog/export/get?id=814656"
r = requests.get(zip_file_url)
path = io.BytesIO(r.content)
data = pd.read_csv(path, compression="zip",
                   encoding="windows-1251", sep=";")
# for downloaded csv
# path = '~/Downloads/data-6267-2020-05-08.csv'
# data = pd.read_csv(file_path, encoding="windows-1251", sep=";")

# Data preprocess
months = {
    "Январь": 1,
    "Февраль": 2,
    "Март": 3,
    "Апрель": 4,
    "Май": 5,
    "Июнь": 6,
    "Июль": 7,
    "Август": 8,
    "Сентябрь": 9,
    "Октябрь": 10,
    "Ноябрь": 11,
    "Декабрь": 12,
}

data["Month"] = data.Month.apply(lambda x: months[x])
data['Date'] = data.apply(lambda x: date(int(x['Year']), int(x['Month']), 1), axis=1)
data['Mon'] = data.Date.apply(lambda d: d.strftime("%b"))
data['Periods'] = data.Year.apply(lambda x: str(x) if x == 2010 or x == 2020 else '2011-2019')


# Data plotting
# Catplot with mean and ci for 2011-2019
sns.set(style="darkgrid")

g = sns.catplot(x="Mon", y="StateRegistrationOfDeath", kind="bar",
                hue="Periods", data=data, palette="Set2",
                legend="full", ci=99.999)
g.fig.suptitle('Monthly death rate in Moscow (Y-Y)')
leg = g._legend
leg.set_bbox_to_anchor([1, 0.9])
plt.show()

fig = g.fig
fig.savefig('moscow_data_stats.png')

# Histogram of monthly cases
fig1 = plt.figure()
skew = round(data.StateRegistrationOfDeath.skew(),2)
std = int(data.StateRegistrationOfDeath.std())
mean = int(data.StateRegistrationOfDeath.mean())
title = f"Monthly cases hist ({mean} +- {std}, skewness {skew})"
ax = data.StateRegistrationOfDeath.plot(bins=50, kind="hist", density=True,
                                        title=title)
data.StateRegistrationOfDeath.plot(kind="kde", ax=ax)
ax.axvline(data.StateRegistrationOfDeath.iloc[-1],
           color='red')
plt.show()
fig1.savefig('moscow_data_hist.png')

# IQT boxplot
fig2 = plt.figure()
g1 = sns.boxplot(x="Mon", y="StateRegistrationOfDeath", data=data)
g1.set_title('Monthly death rate in Moscow (Y-Y)')

plt.show()
fig2.savefig('moscow_data_boxplots.png')
