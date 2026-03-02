import streamlit as st
import re
import json
import ast
import pandas as pd
from time import sleep
from datetime import date, timedelta
from io import BytesIO
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
def extract_type(text):
    """
    Trích xuất 'type' từ chuỗi JSON-like.
    Nếu text không hợp lệ hoặc không có key 'type' thì trả về [] (list rỗng).
    """
    if not text or not isinstance(text, str):
        return []

    # Bỏ ký hiệu code block nếu có
    clean = text.replace("```json", "").replace("```", "").strip()

    try:
        data = json.loads(clean)  # thử parse JSON chuẩn
    except Exception:
        try:
            data = ast.literal_eval(clean)  # thử parse dict kiểu Python
        except Exception:
            return []  # nếu vẫn lỗi thì bỏ qua

    # Nếu không có key "type" hoặc type không phải list → []
    type_val = data.get("type") if isinstance(data, dict) else None
    if not isinstance(type_val, list):
        return []

    # Ép mọi phần tử thành string
    return [str(x) for x in type_val]

def clean_special_only(text):
    if not isinstance(text, str):
        return text  # giữ nguyên nếu không phải string
    # nếu chỉ chứa ký tự không phải chữ hoặc số
    if re.fullmatch(r'[^a-zA-Z0-9]+', text):
        return ''
    return text


def clean_for_streamlit(df: pd.DataFrame) -> pd.DataFrame:
    df_clean = df.copy()
    for col in df_clean.columns:
        if df_clean[col].dtype == 'object':
            df_clean[col] = df_clean[col].apply(
                lambda x: str(x) if isinstance(x, (list, dict, set)) 
                else (str(x) if pd.notna(x) else '')
            )
    return df_clean


def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Data")
    return output.getvalue()



st.set_page_config(page_title="Báo cáo", page_icon=":iphone:")
st.title("1. Up data")
st.subheader("Nhập ngày:")
date = st.text_input("Nhập ngày hôm nay dữ liệu dạng yyyymmdd : ",)
#date1 = st.text_input("Nhập ngày hôm qua dữ liệu dạng yyyymmdd : ",)
#with st.sidebar:  

if not date:
    date='Chưa nhập ngày'

st.subheader("Up tin báo:")
uploaded_file_tinbao = st.file_uploader("Up file excel TIN BÁO ngày hôm nay:", type=["xlsx", "xls"])

if uploaded_file_tinbao is not None:
    try:
        df_tinbao = pd.read_excel(uploaded_file_tinbao,skiprows=5,usecols="A,B,E")      # chỉ lấy cột A, B, E
        df_tinbao.columns = ["STT", "Tên đơn vị", "Tổng"]
        df_tinbao["Tên Khu vực"] = df_tinbao["Tên đơn vị"].apply(
            lambda x: x[x.find("Khu vực"):].strip()
            if isinstance(x, str) and "Khu vực" in x
            else "No"
        )

        df_tinbao["Tên tỉnh"] = df_tinbao["Tên Khu vực"].apply(
            lambda x: x.split("-", 1)[1].strip()
            if isinstance(x, str) and "-" in x
            else "No"
        )
        df_tinbao['Ngay']=date
        df_tinbao['Type']='Tổng tin báo'
        st.success("File đã được tải lên thành công!")
        st.write("Dữ liệu preview:")
        df_tinbao = clean_for_streamlit(df_tinbao)
        st.dataframe(df_tinbao)
    except Exception as e:
        st.error(f"Lỗi khi đọc file: {e}")   
st.subheader("Up truy tố:")
uploaded_file_truyto = st.file_uploader("Up file excel TRUY TỐ ngày hôm nay:", type=["xlsx", "xls"])

if uploaded_file_truyto is not None:
    try:
        df_truyto = pd.read_excel(uploaded_file_truyto,skiprows=5,usecols="A,B,E")      # chỉ lấy cột A, B, E
        df_truyto.columns = ["STT", "Tên đơn vị", "Tổng"]
        df_truyto["Tên Khu vực"] = df_truyto["Tên đơn vị"].apply(
            lambda x: x[x.find("Khu vực"):].strip()
            if isinstance(x, str) and "Khu vực" in x
            else "No"
        )

        df_truyto["Tên tỉnh"] = df_truyto["Tên Khu vực"].apply(
            lambda x: x.split("-", 1)[1].strip()
            if isinstance(x, str) and "-" in x
            else "No"
        )
        df_truyto['Ngay']=date
        df_truyto['Type']='Tổng truy tố'

        st.success("File đã được tải lên thành công!")
        st.write("Dữ liệu preview:")
        df_truyto = clean_for_streamlit(df_truyto)
        st.dataframe(df_truyto)
    except Exception as e:
        st.error(f"Lỗi khi đọc file: {e}")
st.subheader("Up xet xử:")
uploaded_file_xetxu = st.file_uploader("Up file excel XÉT XỬ ngày hôm nay:", type=["xlsx", "xls"])

if uploaded_file_xetxu is not None:
    try:
        df_xetxu = pd.read_excel(uploaded_file_xetxu,skiprows=5,usecols="A,B,C,D,E,F")      # chỉ lấy cột A, B, E
        df_xetxu.columns = ["STT", "Tên đơn vị", "Đã nhập","Đã thụ lý","Đang giải quyết","Đã giải quyết"]
        df_xetxu['Tổng']=df_xetxu["Đã nhập"].fillna(0) + df_xetxu["Đã thụ lý"].fillna(0)+df_xetxu["Đang giải quyết"].fillna(0) + df_xetxu["Đã giải quyết"].fillna(0)

        df_xetxu["Tên Khu vực"] = df_xetxu["Tên đơn vị"].apply(
            lambda x: x[x.find("Khu vực"):].strip()
            if isinstance(x, str) and "Khu vực" in x
            else "No"
        )

        df_xetxu["Tên tỉnh"] = df_xetxu["Tên Khu vực"].apply(
            lambda x: x.split("-", 1)[1].strip()
            if isinstance(x, str) and "-" in x
            else "No"
        )
        df_xetxu['Ngay']=date
        df_xetxu['Type']="Tổng xét xử"
        st.success("File đã được tải lên thành công!")
        st.write("Dữ liệu preview:")
        df_safe = clean_for_streamlit(df_xetxu)
        st.dataframe(df_xetxu)
    except Exception as e:
        st.error(f"Lỗi khi đọc file: {e}")

st.subheader("Up history data:")
uploaded_file_his = st.file_uploader("Up file excel hisrory:", type=["xlsx", "xls"])

if uploaded_file_his is not None:
    try:
        df_his = pd.read_excel(uploaded_file_his)
        df_his['Ngay']=df_his['Ngay'].astype(str)
        date_max=df_his[df_his.Ngay<'20990000'].Ngay.max()
        date_min=df_his.Ngay.min()
        st.success("File đã được tải lên thành công!")
        st.write(f"Dữ liệu preview: từ ngày {date_min} đến ngày {date_max}")
        df_his = clean_for_streamlit(df_his)
        st.dataframe(df_his)
    except Exception as e:
        st.error(f"Lỗi khi đọc file: {e}") 
else:
    df_his=pd.DataFrame()

st.title("2. Báo cáo")

st.set_page_config(layout="wide")

# if not api_key2:
#     st.info("Hãy nhập key trước khi sử dụng.", icon="🗝️")

# else:


if st.button("Nhấn vào đây để xuất báo cáo"):
    try:
        st.write("Processing...")
        #===================================================================================================
        df_tinbao=df_tinbao[df_tinbao['Tên Khu vực']!="No"][['Tên Khu vực','Tên tỉnh','Ngay','Type','Tổng']]
        df_truyto=df_truyto[df_truyto['Tên Khu vực']!="No"][['Tên Khu vực','Tên tỉnh','Ngay','Type','Tổng']]
        df_xetxu=df_xetxu[df_xetxu['Tên Khu vực']!="No"][['Tên Khu vực','Tên tỉnh','Ngay','Type','Tổng']]
        
        df_all = pd.concat([df_tinbao, df_truyto, df_xetxu],axis=0, ignore_index=True)

        df_his=pd.concat((df_his,df_all),axis=0,ignore_index=True)
        df_his = df_his.sort_values(
                                        by=["Tên tỉnh", "Tên Khu vực"],
                                        ascending=[True, True]
                                    )
        df_his['Tên Khu vực'] = df_his['Tên Khu vực'].str.replace('Thành phố ', '', regex=False)
        df_his["Tên tỉnh"] = df_his["Tên Khu vực"].apply(
            lambda x: x.split("-", 1)[1].strip()
            if isinstance(x, str) and "-" in x
            else "No"
        )
        df_his=df_his.drop_duplicates()

        st.subheader("Bảng lịch sử lưu lại để upload hôm sau:")
        

        st.dataframe(df_his)
        #=======================================
        excel_data_his = to_excel(df_his)

        st.download_button(
            label="📥 Down bảng history (.xlsx)",
            data=excel_data_his,
            file_name=f"history_data_{date}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        #===================================================================================================
        # st.subheader("Bảng lịch sử pivot:")
        # df_his1 = df_his.sort_values(["Tên Khu vực", "Type", "Ngay"])
        # df_his1["Hiệu"] = (
        #     df_his1.groupby(["Tên Khu vực", "Type"])["Tổng"]
        #     .diff()
        # )
 
        # df_his1=df_his1[(df_his1.Ngay>date_min)]
        # df_pivot = pd.pivot_table(
        #     df_his1,
        #     index="Tên Khu vực",
        #     columns=["Type", "Ngay"],
        #     values="Hiệu",
        #     aggfunc="sum"   # phòng khi có trùng dữ liệu
        # )
        # df_hieu = df_pivot.reset_index()
        # df_hieu.columns = [
        #     "_".join(map(str, col)).strip("_")
        #     if isinstance(col, tuple)
        #     else col
        #     for col in df_hieu.columns
        # ]
        # df_hieu['Tên tỉnh']=df_hieu["Tên Khu vực"].apply(
        #     lambda x: x.split("-", 1)[1].strip()
        #     if isinstance(x, str) and "-" in x
        #     else "No"
        # )
        # df_hieu=df_hieu.sort_values(
        #                                 by=["Tên tỉnh", "Tên Khu vực"],
        #                                 ascending=[True, True]
        #                             )
        # st.dataframe(df_hieu)

        # #===================================
        # excel_data_hieu = to_excel(df_hieu)    
        # st.download_button(
        #     label="📥 Download bảng history pivot (.xlsx)",
        #     data=excel_data_hieu,
        #     file_name=f"history_hieu_{date}.xlsx",
        #     mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        # )

        #=======================================================================================
        st.subheader("Bảng báo cáo:")
        df_his1=df_his[(df_his.Ngay>=date_max)]
        df_pivot = pd.pivot_table(
            df_his1,
            index="Tên Khu vực",
            columns=["Type", "Ngay"],
            values="Tổng",
            aggfunc="sum"   # phòng khi có trùng dữ liệu
        )
   
        df_export = df_pivot.reset_index()
        df_export.columns = [
            "_".join(map(str, col)).strip("_")
            if isinstance(col, tuple)
            else col
            for col in df_export.columns
        ]
        df_export['Tên tỉnh']=df_export["Tên Khu vực"].apply(
            lambda x: x.split("-", 1)[1].strip()
            if isinstance(x, str) and "-" in x
            else "No"
        )
        df_export=df_export.sort_values(
                                        by=["Tên tỉnh", "Tên Khu vực"],
                                        ascending=[True, True]
                                    )
        st.dataframe(df_export)

        #===================================
        excel_data_pivot = to_excel(df_export)    
        st.download_button(
            label="📥 Download bảng báo cáo Excel (.xlsx)",
            data=excel_data_pivot,
            file_name=f"baocao_data_{date}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
    except Exception as err:
        placeholder = st.empty()
        placeholder.write(err)

st.title("3. Biểu đồ")

ten = st.text_input("Nhập tên biểu đồ : ",)
loai = st.text_input("Nhập loại biểu đồ tỉnh/khu vực : ",)
uploaded_file = st.file_uploader("Upload file Excel", type=["xlsx"])


if uploaded_file is not None:
    try:
        df = pd.read_excel(uploaded_file)
        df.columns = [col.strip() for col in df.columns]

        required_cols = ["Vùng", "Số mới nhập", "Tỷ lệ"]

        if not all(col in df.columns for col in required_cols):
            st.error("File phải có đúng 3 cột: Vùng | Số mới nhập | Tỷ lệ")
        else:
            df = df[required_cols]

            # Làm tròn tỷ lệ
            df["Tỷ lệ"] = (pd.to_numeric(df["Tỷ lệ"], errors="coerce") * 100).round()#.astype(int)

            st.dataframe(df, use_container_width=True)

            fig = go.Figure()

            # Biểu đồ cột
            fig.add_trace(
                go.Bar(
                    x=df["Vùng"],
                    y=df["Số mới nhập"],
                    name="Số mới nhập",
                    text=df["Số mới nhập"],
                    textposition="outside"
                )
            )

            # Biểu đồ line
            fig.add_trace(
                go.Scatter(
                    x=df["Vùng"],
                    y=df["Tỷ lệ"],
                    name="Tỷ lệ (%)",
                    mode="lines+markers+text",
                    text=df["Tỷ lệ"].astype(str) + "%",
                    textposition="top center",
                    textfont=dict(color="red"),
                    line=dict(color="red",width=1),
                    marker=dict(color="red"),
                    yaxis="y2"
                )
            )

            fig.update_layout(
                title=dict(
                    text=ten,
                    x=0.5,
                    xanchor="center"
                ),
                xaxis=dict(
                    title=loai,
                    showgrid=False
                ),
                yaxis=dict(
                    title="Số mới nhập",
                    showgrid=False,
                    zeroline=False
                ),
                yaxis2=dict(
                    title="Tỷ lệ (%)",
                    overlaying="y",
                    side="right",
                    showgrid=False,
                    zeroline=False
                ),
                legend=dict(
                    orientation="h",
                    yanchor="top",
                    y=-0.25,
                    xanchor="center",
                    x=0.5
                ),
                margin=dict(t=80, b=80),
                height=600
            )

            st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"Lỗi khi đọc file: {e}")

st.title("4. Biểu đồ (không có %)")

ten1 = st.text_input("Nhập tên chart : ")
loai1 = st.text_input("Nhập loại chart tỉnh/khu vực : ")
uploaded_file1 = st.file_uploader("Upload Excel", type=["xlsx"])

if uploaded_file1 is not None:
    try:
        df = pd.read_excel(uploaded_file1)
        df.columns = [col.strip() for col in df.columns]

        required_cols = ["Vùng", "Số mới nhập"]

        if not all(col in df.columns for col in required_cols):
            st.error("File phải có đúng 2 cột: Vùng | Số mới nhập")
        else:
            df = df[required_cols]

            # Chuyển Số mới nhập về dạng số
            #df["Số mới nhập"] = pd.to_numeric(df["Số mới nhập"], errors="coerce")

            st.dataframe(df, use_container_width=True)

            fig = go.Figure()

            # Biểu đồ cột
            fig.add_trace(
                go.Bar(
                    x=df["Vùng"],
                    y=df["Số mới nhập"],
                    name="Số mới nhập",
                    text=df["Số mới nhập"],
                    textposition="outside"
                )
            )

            fig.update_layout(
                title=dict(
                    text=ten1,
                    x=0.5,
                    xanchor="center"
                ),
                xaxis=dict(
                    title=loai1,
                    showgrid=False
                ),
                yaxis=dict(
                    title="Số mới nhập",
                    showgrid=False,
                    zeroline=False
                ),
                legend=dict(
                    orientation="h",
                    yanchor="top",
                    y=-0.2,
                    xanchor="center",
                    x=0.5
                ),
                margin=dict(t=80, b=80),
                height=600
            )

            st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"Lỗi khi đọc file: {e}")


#==========================phòng=============================================

st.title("5.Phòng")
st.subheader("Nhập ngày:")
date = st.text_input("aNhập ngày hôm nay dữ liệu dạng yyyymmdd : ",)
st.subheader("Up tin báo:")
uploaded_file_tinbao = st.file_uploader("aUp file excel TIN BÁO ngày hôm nay:", type=["xlsx", "xls"])

if uploaded_file_tinbao is not None:
    try:
        df_tinbao = pd.read_excel(uploaded_file_tinbao,skiprows=5,usecols="A,B,E")      # chỉ lấy cột A, B, E
        df_tinbao.columns = ["STT", "Tên đơn vị", "Tổng"]

        df_tinbao["Tên Khu vực"] = df_tinbao["Tên đơn vị"].apply(
            lambda x: x[x.find("Khu vực"):].strip()
            if isinstance(x, str) and "Khu vực" in x
            else x
        )

        df_tinbao["Tên tỉnh"] = df_tinbao["Tên Khu vực"].apply(
            lambda x: x.split("-", 1)[1].strip()
            if isinstance(x, str) and "-" in x
            else "1_"
        )

        df_tinbao["STT"] = df_tinbao["STT"].fillna(0)
        df_tinbao["group"] = (df_tinbao["STT"] < df_tinbao["STT"].shift()).cumsum()
        df_tinbao["city"] = df_tinbao.groupby("group")["Tên tỉnh"].transform("max")
        df_tinbao=df_tinbao[df_tinbao['Tên Khu vực'].str.contains("Phòng Công tố")]

        df_tinbao['Ngay']=date
        df_tinbao['Type']='Tổng tin báo'
        
        st.success("File đã được tải lên thành công!")
        st.write("Dữ liệu preview:")
        df_tinbao = clean_for_streamlit(df_tinbao)
        st.dataframe(df_tinbao)
        df_tinbao_tinh = (
                            df_tinbao
                                .groupby(["city", "Ngay", "Type"], as_index=False)["Tổng"]
                                .sum()
                        )
        df_tinbao_tinh = df_tinbao_tinh.sort_values("city")
        df_tinbao_tinh = clean_for_streamlit(df_tinbao_tinh)
        st.dataframe(df_tinbao_tinh)

    except Exception as e:
        st.error(f"Lỗi khi đọc file: {e}")   

        st.download_button(
            label="📥 Down bảng history (.xlsx)",
            data=excel_data_his,
            file_name=f"history_data_{date}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
st.subheader("aUp truy tố:")
uploaded_file_truyto = st.file_uploader("aUp file excel TRUY TỐ ngày hôm nay:", type=["xlsx", "xls"])

if uploaded_file_truyto is not None:
    try:
        df_truyto = pd.read_excel(uploaded_file_truyto,skiprows=5,usecols="A,B,E")      # chỉ lấy cột A, B, E
        df_truyto.columns = ["STT", "Tên đơn vị", "Tổng"]
        df_truyto["Tên Khu vực"] = df_truyto["Tên đơn vị"].apply(
            lambda x: x[x.find("Khu vực"):].strip()
            if isinstance(x, str) and "Khu vực" in x
            else x
        )

        df_truyto["Tên tỉnh"] = df_truyto["Tên Khu vực"].apply(
            lambda x: x.split("-", 1)[1].strip()
            if isinstance(x, str) and "-" in x
            else "1_"
        )
        df_truyto["STT"] = df_truyto["STT"].fillna(0)
        df_truyto["group"] = (df_truyto["STT"] < df_truyto["STT"].shift()).cumsum()
        df_truyto["city"] = df_truyto.groupby("group")["Tên tỉnh"].transform("max")
        df_truyto=df_truyto[df_truyto['Tên Khu vực'].str.contains("Phòng Công tố")]


        df_truyto['Ngay']=date
        df_truyto['Type']='Tổng truy tố'

        st.success("File đã được tải lên thành công!")
        st.write("Dữ liệu preview:")
        df_truyto = clean_for_streamlit(df_truyto)
        st.dataframe(df_truyto)
        df_truyto_tinh = (
                            df_truyto
                                .groupby(["city", "Ngay", "Type"], as_index=False)["Tổng"]
                                .sum()
                        )
        df_truyto_tinh = df_truyto_tinh.sort_values("city")
        df_truyto_tinh = clean_for_streamlit(df_truyto_tinh)
        st.dataframe(df_truyto_tinh)

    except Exception as e:
        st.error(f"Lỗi khi đọc file: {e}")

st.subheader("aUp xet xử:")
uploaded_file_xetxu = st.file_uploader("aUp file excel XÉT XỬ ngày hôm nay:", type=["xlsx", "xls"])

if uploaded_file_xetxu is not None:
    try:
        df_xetxu = pd.read_excel(uploaded_file_xetxu,skiprows=5,usecols="A,B,C,D,E,F")      # chỉ lấy cột A, B, E
        df_xetxu.columns = ["STT", "Tên đơn vị", "Đã nhập","Đã thụ lý","Đang giải quyết","Đã giải quyết"]
        df_xetxu['Tổng']=df_xetxu["Đã nhập"].fillna(0) + df_xetxu["Đã thụ lý"].fillna(0)+df_xetxu["Đang giải quyết"].fillna(0) + df_xetxu["Đã giải quyết"].fillna(0)

        df_xetxu["Tên Khu vực"] = df_xetxu["Tên đơn vị"].apply(
            lambda x: x[x.find("Khu vực"):].strip()
            if isinstance(x, str) and "Khu vực" in x
            else x
        )

        df_xetxu["Tên tỉnh"] = df_xetxu["Tên Khu vực"].apply(
            lambda x: x.split("-", 1)[1].strip()
            if isinstance(x, str) and "-" in x
            else "1_"
        )

        df_xetxu["STT"] = df_xetxu["STT"].fillna(0)
        df_xetxu["group"] = (df_xetxu["STT"] < df_xetxu["STT"].shift()).cumsum()
        df_xetxu["city"] = df_xetxu.groupby("group")["Tên tỉnh"].transform("max")
        df_xetxu=df_xetxu[df_xetxu['Tên Khu vực'].str.contains("Phòng Công tố")]


        df_xetxu['Ngay']=date
        df_xetxu['Type']="Tổng xét xử"
        st.success("File đã được tải lên thành công!")
        st.write("Dữ liệu preview:")
        df_safe = clean_for_streamlit(df_xetxu)
        st.dataframe(df_xetxu)
        df_xetxu_tinh = (
                            df_xetxu
                                .groupby(["city", "Ngay", "Type"], as_index=False)["Tổng"]
                                .sum()
                        )
        df_xetxu_tinh = df_xetxu_tinh.sort_values("city")
        df_xetxu_tinh = clean_for_streamlit(df_xetxu_tinh)
        st.dataframe(df_xetxu_tinh)

    except Exception as e:
        st.error(f"Lỗi khi đọc file: {e}")

# st.subheader("Up history data:")
# uploaded_file_his = st.file_uploader("Up file excel hisrory:", type=["xlsx", "xls"])

# if uploaded_file_his is not None:
#     try:
#         df_his = pd.read_excel(uploaded_file_his)
#         df_his['Ngay']=df_his['Ngay'].astype(str)
#         date_max=df_his[df_his.Ngay<'20990000'].Ngay.max()
#         date_min=df_his.Ngay.min()
#         st.success("File đã được tải lên thành công!")
#         st.write(f"Dữ liệu preview: từ ngày {date_min} đến ngày {date_max}")
#         df_his = clean_for_streamlit(df_his)
#         st.dataframe(df_his)
#     except Exception as e:
#         st.error(f"Lỗi khi đọc file: {e}") 
# else:
#     df_his=pd.DataFrame()