from sql_app.models import Race
from sql_app.services import InitDataRaceModel

races_in_competition_df = InitDataRaceModel("ccb6e115-c342-4948-b8e6-4525ff6d7832", Race)
races_in_competition_df = races_in_competition_df.transform()

set_names_races = {i for i in races_in_competition_df["event.DisplayName"]}

dict_country = {}
list_names = []

for row in range(len(races_in_competition_df["racePhase.DisplayName"])):
    if races_in_competition_df["racePhase.DisplayName"][row] == "Final":
        x = races_in_competition_df["id"][row]
        y = races_in_competition_df["event.DisplayName"][row]
        list_names.append((y, x))

dict_country.update(tuple(list_names))

if __name__ == '__main__':
    print(set_names_races)
    print(dict_country)



