import pandas as pd
import folium
from folium.plugins import MarkerCluster
import matplotlib.pyplot as plt


# Συνάρτηση λήψης σεισμολογικών δεδομένων από το ΙΤΣΑΚ για κάποιο έτος
def get_earthquake_data(year):
    # Μορφή κάθε συνδέσμου ανά έτος (2013-2023)
    url = f"https://shakemaps.itsak.gr/archive/{year}.html"

    # Τα δεδομένα είναι σε μορφή HTML table
    tables = pd.read_html(url, match='Name/Epicenter', header=0)
    # print(tables)
    # print(type(tables))

    # Το tables είναι σε μορφή λίστας οπότε κρατώ το πρώτο στοιχείο
    table = tables[0]
    # print(table)

    return table


# Ορίζω τα υπό μελέτη έτη
years = list(range(2013, 2023))

# Ορίζω λίστα για όλα τα δεδομένα
all_earthquake_data = []

# Παίρνω τα σεισμολογικά δεδομένα για όλα τα έτη
for year in years:
    earthquake_data = get_earthquake_data(year)
    all_earthquake_data.append(earthquake_data)

# Συνδυάζω όλα τα δεδομένα σε ένα DataFrame
combined_data = pd.concat(all_earthquake_data, ignore_index=True)

# Τυπώνω τα: συνολικός αριθμός γεγονότων, μέσο μέγεθος σεισμού, συντεταγμένες του ορθογωνίου
total_events = len(combined_data)  # συνολικός αριθμός γεγονότων
print(f"Συνολικός αριθμός γεγονότων: {total_events}")
average_magnitude = combined_data['Mag'].mean()  # μέσο μέγεθος σεισμού
print(f"Μέσο μέγεθος σεισμού: {average_magnitude}")
min_latitude, max_latitude = combined_data['Lat'].min(), combined_data['Lat'].max()  # γεωγραφικό πλάτος
min_longitude, max_longitude = combined_data['Lon'].min(), combined_data['Lon'].max()  # γεωγραφικό μήκος
print(
    f"Συντεταγμένες του ορθογωνίου στον χάρτη: ({min_latitude}, {min_longitude}) to ({max_latitude}, {max_longitude})")

# Δημιουργώ το ραβδόγραμμα με τα 10 ισχυρότερα γεγονότα
top_10_events = combined_data.nlargest(10, 'Mag')  # επιλέγω τα top 10 ως προς Mag


# Συνάρτηση προσθήκης ετικέτας στις στήλες του ραβδογράμματος
def create_label(row):
    return f"{row['Name/Epicenter']} ({row['Date']})"


# Προσθέτω τα labels
top_10_events['Label'] = top_10_events.apply(create_label, axis=1)

# Σχηματίζω το ραβδόγραμμα
ax = top_10_events.plot(kind='bar', x='Label', y='Mag', legend=False, title='Top 10 Strongest Earthquakes')
plt.xlabel('Earthquake')
plt.ylabel('Magnitude')
ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')
plt.subplots_adjust(bottom=0.4)
plt.show()

# Προαιρετικά: Εμφανίζω τα γεγονότα με Meg > 5.5 σε έναν χάρτη με το Folium

# Επιλογή γεγονότων μεγέθους > 5.5
selected_events = combined_data[combined_data['Mag'] > 5.5]
# print(selected_events)

# Υπολογίζω το μέσο γεωγραφικό πλάτος και μήκος για να κεντράρω σε αυτά
map_center = [selected_events['Lat'].mean(), selected_events['Lon'].mean()]

# Σχηματίζω τον χάρτη
mymap = folium.Map(location=map_center, zoom_start=6)
marker_cluster = MarkerCluster().add_to(mymap)  # ομαδοποίηση κοντινών γεγονότων

# Προσθέτω κυκλικό δείκτη για κάθε γεγονός, όπου η ακτίνα είναι ανάλογη του μεγέθους
for index, row in selected_events.iterrows():
    folium.CircleMarker(location=[row['Lat'], row['Lon']],
                        radius=row['Mag'],
                        color='red',
                        fill=True,
                        fill_color='red').add_to(marker_cluster)

mymap.save('earthquake_map.html')
