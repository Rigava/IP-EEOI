import streamlit as st
import pandas as pd
import numpy as np

upload1 = st.file_uploader("Choose the outgoing vessel data")
# df=pd.read_csv('Data For Outgoing vessels.csv')
df=pd.read_csv(upload1)
df['DistanceWeighted Utilisation']=df['DistanceWeighted Utilisation'].str.replace('%','').astype(float)
upload2 = st.file_uploader("Choose the fleet data")
# df_fleet = pd.read_csv('Data For Fleet.csv')
df_fleet =pd.read_csv(upload2)
df_fleet['DistanceWeighted Utilisation']=df_fleet['DistanceWeighted Utilisation'].str.replace('%','').astype(float)
def predict_cii(deadweight):
    return 1984 * deadweight**(-0.489)

def calculate_future_cii(deadweight, start_year, end_year):
    years = range(start_year, end_year + 1)
    reduction_factors = [1,2,3,5,7,9,11,13,17,19,21]
    data = {'Year': [], 'CII': [], 'Improved_CII': []}
    for i, year in enumerate(years):
        cii = predict_cii(deadweight)
        reduction_factor = reduction_factors[i] / 100
        improved_cii = cii * (1 - reduction_factor)
        data['Year'].append(year)
        data['CII'].append(cii)
        data['Improved_CII'].append(improved_cii)
        df = pd.DataFrame(data)
    return df

def main():
    st.title("New Building Impact")
    st.subheader("Without data you are just another person with opinion")
    if df:
        st.write(df)
        # Get input from the user
        dwt = st.number_input("Enter Deadweight of the vessel", min_value=5000.0)
        cii = predict_cii(dwt)
        i_year = st.number_input("Enter incoming year of the vessel", min_value=2020.0)
        i_vessel = st.number_input("Enter number of incoming vessel", min_value=1.0)
        start_year = 2020
        end_year = 2030
        df_cii = calculate_future_cii(dwt,start_year, end_year)
        # st.write(df_cii.loc[df_cii['Year'] == i_year,'Improved_CII'].values[0])
        i_cii =  df_cii.loc[df_cii['Year'] == i_year,'Improved_CII'].values[0]
        catA_cii = .73 * i_cii  
        st.write(f" Proposed AER for incoming vessel based on category A is: {catA_cii:.1f}")
        #  CASE 1- IF THE PAYLOAD IS SAME AS OUTGOING
        payload = df['avg Payload per Voyage'].values[0]
        i_util = payload/dwt
        i_eeoi = catA_cii/i_util
        st.write(f"As per the outgoing payload {payload:.1f} tons the utilisation assumed for incoming is {i_util:.1f} and the eeoi is {i_eeoi:.1f}")
        i_transportWork = df['avg TW per ship'].values[0]
        i_co2emission = i_transportWork * i_eeoi/10**6
        reduction = df['avg tCO2 per ship'].values[0] - i_co2emission
        totalred = reduction * i_vessel
        st.write(f" The absolute emisson based on the eeoi of {i_eeoi:.1f} is {i_co2emission:.2f} tons co2 with reduction of {reduction:.2f} tons")
        st.write(f" The total reduction for {i_vessel} vessels is {totalred:.2f}")
    # Find the Fleet level reduction
    if df_fleet:
        st.write(df_fleet) 
        tco2 = df_fleet['CO2 (in tons)'].values[0]
        tw = df_fleet['Transport work per Mn'].values[0]
        newtco2 = df_fleet['CO2 (in tons)'].values[0] - totalred
        eeoi = tco2/tw
        eeoi_new = newtco2/tw
        st.write (f"The fleet co2 emission reduced from {tco2:.1f} to {newtco2:.1f}")
        st.write (f"The fleet eeoi reduced from {eeoi:.2f} to {eeoi_new:.2f}")

    # Find the Fleet level reduction
    st.write(df_fleet) 
    tco2 = df_fleet['CO2 (in tons)'].values[0]
    tw = df_fleet['Transport work per Mn'].values[0]
    newtco2 = df_fleet['CO2 (in tons)'].values[0] - totalred
    eeoi = tco2/tw
    eeoi_new = newtco2/tw
    st.write (f"The fleet co2 emission reduced from {tco2:.1f} to {newtco2:.1f}")
    st.write (f"The fleet eeoi reduced from {eeoi:.2f} to {eeoi_new:.2f}")

if __name__ == "__main__":
    main()
