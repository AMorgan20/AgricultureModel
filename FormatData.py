import pandas as pd
import statistics as st
import matplotlib.pyplot as plt
import seaborn as sns
#from ExcelManager import foodsCalories

# agExtServices = pd.read_stata('./Datasets/01.AgriculturalExtensionServices.dta')
# agProdLvl1 = pd.read_stata('./Datasets/02.AgriculturalProduction_level_1.dta')
# agProdLvl2 = pd.read_stata('./Datasets/03.AgriculturalProduction_plot_repeat_begin_level_2.dta')
# agProdLvl3 = pd.read_stata('./Datasets/04.AgriculturalProduction_crop_level_3.dta')
# agProdLvl4 = pd.read_stata('./Datasets/05.AgriculturalProduction_group_crop_i_croptype_level_4.dta')
# agSubsidyCard = pd.read_stata('./Datasets/06.AgriculturalSubsidyCard.dta')

# cropsLvl1 = pd.read_stata('./Datasets/12.Crops_level_1.dta')
# cropsLvl2 = pd.read_stata('./Datasets/13.Crops_plot_repeat_begin_level_2.dta')
# cropsLvl3 = pd.read_stata('./Datasets/14.Crops_crop_level_3.dta')
# cropsLvl4 = pd.read_stata('./Datasets/15.Crops_group_crop_i_croptype_level_4.dta')

# hhCompLvl1 = pd.read_stata('./Datasets/HouseholdComposition_level_1.dta')
# hhCompLvl2 = pd.read_stata('./Datasets/HouseholdComposition_members_level_2.dta')

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
# TODO: Create conversions for all the units into kg (make some generalizations)
foodsList = pd.DataFrame(fDiary2Link3.food_type_name.unique(), columns=['food_type'])
# The list of different foods which will be used to calculate calories
foodGroups = pd.Series(fDiary2Link3.food_grp_namec.unique())
# TODO: Find the calories for each food
# TODO: Convert all of them to the same units, or have different calorie values for each food?
# Conversion from weight to volume is not the same for each food type. Depending on the food, different units are used

# TODO: Create a dataframe that has a household and 1 group for each food type by week (so it's hh_ID vs week)


foodGroupsHousehold = pd.DataFrame(columns=weekNumbers, index=householdIDLinked)
foodGroupsHousehold = foodGroupsHousehold.fillna(0)
grpFDiary2Link3 = fDiary2Link3.groupby(['hh_ID', 'food_grp_namec', 'week_number'], as_index=False).sum()
# Adds the amount of food for each food group by week and hh_ID
# TODO: Find which unit is common for each type of food, then create another column for units
foodsList.insert(1, 'unit', ' ')

'''for q in foodsList.index:
    for u in fDiary2Link3.index:
        tempList = pd.DataFrame()
        if foodsList.loc[q, 'food_type'] == fDiary2Link3.loc[u, 'food_grp_namec']:
            tempList.append(grpFDiary2Link3.loc[u, 'food_type_unit'])
            foodsList.at[q, 'unit'] = st.mode(tempList)'''
# Take the mode of the column, given it is part of q food group
# TODO: Does not work: takes way too long and the unit column does not fill
# TODO: Solution?- try sorting fDiary2Link3 by food group names, then splitting it into separate dataframes


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
plt.show()

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
