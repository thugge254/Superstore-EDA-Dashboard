import streamlit as st
import plotly.express as px
import pandas as pd
import os
import warnings
warnings.filterwarnings("ignore")

st.set_page_config(page_title='Superstore Dashboard', page_icon=':bar_chart:', layout='wide')

st.title(" :bar_chart: Superstore EDA Dashboard")
st.markdown("<style>div.block-container{padding-top:2rem;}</style>", unsafe_allow_html=True)

f1 = st.file_uploader(":file_folder: Upload a file", type=(["csv","txt","xlsx","xls"]))
if f1 is not None:
    filename = f1.name
    st.write(filename)
    df = pd.read_excel(filename, engine='xlrd')
else:
    os.chdir(r"C:\Users\Moses\Dashboard in Python\SuperStore Dashboard")
    df = pd.read_excel("Superstore.xls", engine='xlrd')
col1, col2 = st.columns((2))
df["Order Date"] = pd.to_datetime(df["Order Date"])
# Getting min and max date
startDate = df["Order Date"].min()
endDate = df["Order Date"].max()

with col1:
    date1 = pd.to_datetime(st.date_input("Start Date", startDate))

with col2:
    date2 = pd.to_datetime(st.date_input("End Date", endDate))

df = df[(df["Order Date"]>=date1) & (df["Order Date"]<=date2)].copy()

st.sidebar.header("Choose your filter:")

# create for region
region = st.sidebar.multiselect("Select region(s)", df["Region"].unique())
if not region:
    df2 = df.copy()
else:
    df2 = df[df["Region"].isin(region)]

# create for state
state = st.sidebar.multiselect("Select state(s)", df2["State"].unique())
if not region:
    df3 = df2.copy()
else:
    df3 = df2[df2["State"].isin(state)]

# create for city
city = st.sidebar.multiselect("Select city(s)", df3["City"].unique())
if not city:
    df5 = df3.copy()
else:
    df5 = df3[df3["City"].isin(city)]

 # filter the data based on Region, State and City
if not region and not state and not city:
    filtered_df = df
elif not state and not city:
    filtered_df = df[df["Region"].isin(region)]
elif not region and not city:
    filtered_df = df[df["State"].isin(state)]
elif state and city:
    filtered_df = df3[df["State"].isin(state) & df3["City"].isin(city)]
elif region and city:
    filtered_df = df3[df["State"].isin(region) & df3["City"].isin(city)]
elif region and state:
    filtered_df = df3[df["State"].isin(region) & df3["City"].isin(state)]
elif city:
    filtered_df = df3[df3["City"].isin(city)]
else:
    filtered_df = df3[df3["Region"].isin(region) & df3["State"].isin(state) & df3["City"].isin(city)] 

category_df = filtered_df.groupby(by = ["Category"], as_index = False)["Sales"].sum()

with col1:
    st.subheader("Category-wise Sales")
    fig = px.bar(category_df,x="Category",y="Sales",text=["${:,.2f}".format(x) for x in category_df["Sales"]],template="seaborn")
    px.bar(category_df, x="Category", y="Sales",text=["${:,.2f}".format(x) for x in category_df["Sales"]], template="seaborn")
    st.plotly_chart(fig, use_container_width=True, height = 200)

with col2:
     st.subheader("Region-wise Sales")
     fig = px.pie(filtered_df, values="Sales", names="Region", hole=0.5)
     fig.update_traces(text = filtered_df["Region"], textposition = "outside", textinfo="percent+label")
     st.plotly_chart(fig, use_container_width=True)

cl1, cl2 = st.columns(2)
with cl1:
    with st.expander("Category_ViewData"):
        st.write(category_df.style.background_gradient(cmap = "Blues"))
        csv = category_df.to_csv(index = False).encode("utf-8")
        st.download_button(label="Download Category Data",data=csv,
                           file_name="Category_Data.csv",mime="text/csv",
                           help="Click here to download the data as a CSV file")

        
with cl2:
    with st.expander("Region_ViewData"):
        region = filtered_df.groupby(by = "Region", as_index = False)["Sales"].sum()
        st.write(region.style.background_gradient(cmap = "Oranges"))
        csv = category_df.to_csv(index = False).encode("utf-8")
        st.download_button(label="Download Region Data",data=csv,
                           file_name="Region_Data.csv",mime="text/csv",
                           help="Click here to download the data as a CSV file")
        
filtered_df["month_year"] = filtered_df["Order Date"].dt.to_period("M")
st.subheader("Time Series Analysis Plot")
linechart = pd.DataFrame(filtered_df.groupby(filtered_df["month_year"].dt.strftime("%Y : %b"))["Sales"].sum()).reset_index()
fig2 = px.line(linechart, x="month_year", y="Sales", labels={"Sales" : "Amount"},
                height=500, width=1000, template="gridon")
st.plotly_chart(fig2, use_container_width=True)

with st.expander("View Data of the TimeSeries Analysis"):
    st.write(linechart.T.style.background_gradient(cmap="Blues"))
    csv = linechart.to_csv(index=False).encode("utf-8")
    st.download_button("Download the Data", data=csv, file_name="TimeSeries.csv", mime="text/csv")

# create a treemap  chart based on region, category and subcategory
st.markdown(
    "<h3 style='margin-bottom: -1rem;'>Hierarchical view of sales-data using a treemap chart</h3>",
    unsafe_allow_html=True)
fig3 = px.treemap(filtered_df, path=["Region", "Category", "Sub-Category"], values="Sales", 
                  hover_data=["Sales"], color="Sub-Category")
fig3.update_layout(width=800, height=700)
    # Make slice labels inside the pie bigger
fig.update_traces(
        text=filtered_df["Segment"],
        textposition="inside",
        textfont=dict(size=20)  
)
st.plotly_chart(fig3, use_container_width=True, config={'displayModeBar': False})

chart1, chart2 = st.columns((2))
with chart1:
    st.subheader("Segment-wise Sales")
    fig = px.pie(filtered_df, values="Sales", names="Segment", template="gridon")
    fig.update_traces(
        text=filtered_df["Segment"],
        textposition="inside",
        textfont=dict(size=15)  
    )
    fig.update_layout(
        uniformtext=dict(minsize=18, mode='show'),
        legend=dict(
            font=dict(size=18),  
            orientation="h",     
            x=1, xanchor="left"  
        ),
        margin=dict(t=20, b=20, l=20, r=20)
    )
    st.plotly_chart(fig, use_container_width=True)
with chart2:
    st.subheader("Category-wise Sales")
    fig = px.pie(filtered_df, values="Sales", names="Category", template="gridon")
    fig.update_traces(
        text=filtered_df["Category"],
        textposition="inside",
        textfont=dict(size=15)  
    )
    fig.update_layout(
        uniformtext=dict(minsize=18, mode='show'),
        legend=dict(  
            orientation="h",     
            x=1,
            font=dict(size=18)
        ),
        margin=dict(t=20, b=20, l=20, r=20)
    )
    st.plotly_chart(fig, use_container_width=True)

import plotly.figure_factory as ff
st.subheader(":point_right: Month-Wise Subcategory Sales summary")
with st.expander("Summary Table"):
    sample_df = df[0:5][[ "Order Date","Segment","Region", "Category", "Sales", "Profit",
                          "Quantity", "Country", "State", "City"]]
    
    # Format only the numeric columns
    formatted_df = sample_df.copy()
    for col in ["Sales", "Profit", "Quantity"]:
        formatted_df[col] = formatted_df[col].apply(lambda x: f"{x:,.2f}")
    fig = ff.create_table(formatted_df, colorscale="plasma")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("##### Monthly-Wise Subcategory Table")
    filtered_df["month"] = filtered_df["Order Date"].dt.month_name()
    sub_category_Year = pd.pivot_table(data=filtered_df, values="Sales", index="Sub-Category", 
                                       columns="month")
    st.write(sub_category_Year.style.background_gradient(cmap = "Blues"))

# create a scatter plot
data1 = px.scatter(filtered_df, x="Sales", y="Profit", size="Quantity")
data1["layout"].update(title = "A scatter plot showing the relationship between Profit and Sales",
                       titlefont = dict(size = 20), xaxis = dict(title = "Sales", titlefont = dict(size = 19)),
                       yaxis = dict(title = "Profit", titlefont = dict(size = 19)))
st.plotly_chart(data1, use_container_width=True)
with st.expander("View Data"):
    st.write(filtered_df.iloc[:500,1:20:2].style.background_gradient(cmap = "YlOrRd"))

# Download original dataset
csv = df.to_csv(index = False).encode("utf-8")
st.download_button("Download Data", data = csv, file_name="Data.csv",
                   mime="text/csv")




