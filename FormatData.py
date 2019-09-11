import pandas as pd
import statistics as st
import matplotlib.pyplot as plt
import seaborn as sns


hhCompLvl1 = pd.read_stata('./Datasets/HouseholdComposition_level_1.dta')
hhCompLvl2 = pd.read_stata('./Datasets/HouseholdComposition_members_level_2.dta')

fDiaryLvl1 = pd.read_stata('./Datasets/33.FoodDiary_level_1.dta').sort_values(by=['hh_ID']).reset_index(drop=True)
fDiaryLvl2 = pd.read_stata('./Datasets/34.FoodDiary_food_level_2.dta').sort_values(by=['hh_ID', 'food_1_ID',
                                                                                       'food_2_ID'])
fDiaryLvl3 = pd.read_stata('./Datasets/35.Fooddiary_food_foodtype_level_3.dta')
# Reading in the data from stata format into a pandas data frame

fDiaryLvl1.drop(['submissiondate', 'start_time', 'end_time', 'today', 'start_date', 'expiration_date',
                'max_submissions', 'task_value', 'task_length'], axis=1, inplace=True)
fDiaryLvl2.drop(['food_label'], axis=1, inplace=True)
fDiaryLvl3.drop(['food_type_label', 'food_unit_label'], axis=1, inplace=True)
# Removing irrelevant information to this project

fDiary1Link2 = fDiaryLvl1.merge(fDiaryLvl2)
fDiary2Link3 = fDiary1Link2.merge(fDiaryLvl3).sort_values(by=['hh_ID', 'week_number']).reset_index(drop=True)
# Linking the food diary levels using the unique ID numbers

# fDiary2Link3.drop(fDiary2Link3.ix([:,''])
# Deleting a range of columns


householdIDLinked = pd.Series(fDiaryLvl1.hh_ID.unique()).sort_values()
weekNumbers = pd.Series(fDiaryLvl1.week_number.unique()).sort_values()
unitsUsed = pd.Series(fDiaryLvl3.food_type_unit.unique())
foodsList = pd.DataFrame(fDiary2Link3.food_type_name.unique(), columns=['food_type'])
# The list of different foods which will be used to calculate calories
foodGroups = pd.Series(fDiary2Link3.food_grp_namec.unique())
foodsCalories = pd.read_excel('FoodCalories.xlsx', sheet_name='Sheet1')
# Calories for each food
foodsCalories = foodsCalories.fillna(0)
missingCalories = foodsCalories[foodsCalories.calories == 0]


foodGroupsHousehold = pd.DataFrame(columns=weekNumbers, index=householdIDLinked)
foodGroupsHousehold = foodGroupsHousehold.fillna(0)
grpFDiary2Link3 = fDiary2Link3.groupby(['hh_ID', 'food_grp_namec', 'week_number'], as_index=False).sum()
# Adds the amount of food for each food group by week and hh_ID

mask = fDiary2Link3.crowdsource == 'Yes'
noCrowdSource = fDiary2Link3[mask]
crowdSource = fDiary2Link3[~mask]

cSWeekly = crowdSource[crowdSource.recall == 'week']
cSMonthly = crowdSource[crowdSource.recall == 'month']
cSSeasonal = crowdSource[crowdSource.recall == 'season']

noCSWeekly = noCrowdSource[noCrowdSource.recall == 'week']
noCSMonthly = noCrowdSource[noCrowdSource.recall == 'month']
noCSSeasonal = noCrowdSource[noCrowdSource.recall == 'season']


def food_group_sums(food_group, df):
    for z in grpFDiary2Link3.index:
        if grpFDiary2Link3.loc[z, 'food_grp_namec'] == food_group:
            df.at[grpFDiary2Link3.loc[z, 'hh_ID'], grpFDiary2Link3.loc[z, 'week_number']] =\
                grpFDiary2Link3.loc[z, 'food_type_quant']
# Sums the amount of each food by food group per week


meatEggGroup = pd.DataFrame()
food_group_sums('meategg', meatEggGroup)
meatEggGroup = meatEggGroup.sort_index(axis=1).transpose()
vegetablesGroup = pd.DataFrame()
food_group_sums('vegetables', vegetablesGroup)
vegetablesGroup = vegetablesGroup.sort_index(axis=1).transpose()
dairyGroup = pd.DataFrame()
food_group_sums('dairy', dairyGroup)
dairyGroup = dairyGroup.sort_index(axis=1).transpose()

sns.heatmap(meatEggGroup, cmap='PiYG', vmax=500)
# plt.show()
# TODO: Look into how the color pallets work
# TODO: Find a way to differentiate between no response and no food in the graphs
# TODO: Normalize the graphs so it is food/person in each household instead of food/household
# Some households may have more people than others, which is why they receive more food

responseTest = pd.DataFrame(columns=weekNumbers, index=householdIDLinked)
responseTest = responseTest.fillna(0)
# If there is a hh_ID, find its week number and count that, otherwise there was no response
# Set it so the lvl1 gives a 1, the linked gives a 2, and both of them gives a 3
# Does not work as intended because there are multiple responses per week
for y in fDiaryLvl1.index:
    responseTest.at[fDiaryLvl1.loc[y, 'hh_ID'], fDiaryLvl1.loc[y, 'week_number']] = 1

for x in fDiary2Link3.index:
    responseTest.at[fDiary2Link3.loc[x, 'hh_ID'], fDiary2Link3.loc[x, 'week_number']] = 2

testCase = pd.DataFrame(fDiaryLvl3[(fDiaryLvl3['hh_ID'] == 222257)])
