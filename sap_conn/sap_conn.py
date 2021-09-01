from pprint import PrettyPrinter
import logging
import pandas as pd
from pyrfc import Connection
import time

logging.basicConfig(filename='logs.txt', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class main():
    def __init__(self):
        ASHOST='196.254.100.115'
        CLIENT='888'
        SYSNR='00'
        USER='sapadm'
        PASSWD='CHC21adm'
        self.conn = Connection(ashost=ASHOST, sysnr=SYSNR, client=CLIENT, user=USER, passwd=PASSWD)

    def qry(self, Fields, SQLTable, Where = '', MaxRows=50, FromRow=0):
        """A function to query SAP with RFC_READ_TABLE"""

        # By default, if you send a blank value for fields, you get all of them
        # Therefore, we add a select all option, to better mimic SQL.
        if Fields[0] == '*':
            Fields = ''
        else:
            Fields = [{'FIELDNAME':x} for x in Fields] # Notice the format

            # the WHERE part of the query is called "options"
            options = [{'TEXT': x} for x in Where] # again, notice the format

            # we set a maximum number of rows to return, because it's easy to do and
            # greatly speeds up testing queries.
            rowcount = MaxRows

            # Here is the call to SAP's RFC_READ_TABLE
            tables = self.conn.call("RFC_READ_TABLE", QUERY_TABLE=SQLTable, DELIMITER='|', FIELDS = Fields, OPTIONS=options, ROWCOUNT = MaxRows, ROWSKIPS=FromRow)

            # We split out fields and fields_name to hold the data and the column names
            fields = []
            fields_name = []

            data_fields = tables["DATA"]  # pull the data part of the result set
            data_names = tables["FIELDS"]  # pull the field name part of the result set

            headers = [x['FIELDNAME'] for x in data_names] # headers extraction
            long_fields = len(data_fields) # data extraction
            long_names = len(data_names) # full headers extraction if you want it

            # now parse the data fields into a list
            for line in range(0, long_fields):
                fields.append(data_fields[line]["WA"].strip())

            # for each line, split the list by the '|' separator
            fields = [x.strip().split('|') for x in fields]

            # return the 2D list and the headers
            return fields, headers


def getData():
    # Init the class and connect
    # I find this can be very slow to do...
    s = main()
    s_vbak = main()
    s_vbap = main()
    # Choose your fields and table
    fields = ['VBELN', 'WERKS', 'MATNR', 'ERDAT', 'LFIMG', 'VGBEL', 'VGPOS', 'ARKTX'] # VBELN: 611...出貨單號(交貨)
    table = 'LIPS'
    # you need to put a where condition in there... could be anything
    # where = ['EBELN = 4600002086']
    where = ['VBELN <> 0 AND WERKS = \'J150\'']  # AND MATNR  LIKE \'OPROFA\' /杏業的出貨單
    # max number of rows to return
    maxrows = 1000000  # 364244  sap上RFC_READ_TABLE 跑出來的結果

    # starting row to return
    fromrow = 0
    # Pretty Printer
    pp = PrettyPrinter(indent=1)
    # query SAP
    results, headers = s.qry(fields, table, where, maxrows, fromrow)

    # 第2個table做比較用:VBAK
    fields2 = ['VBELN', 'KUNNR']  # LIPS-VGBEL 對上 VBAK-VBELN 銷售文件號碼
    table2 = 'VBAK'
    where2 = ['KUNNR = \'0000018023\'']
    results2, headers2 = s_vbak.qry(fields2, table2, where2, maxrows, fromrow)

    # 第3個table做比較用: VBAP 銷售文件項目資料
    fields3 = ['VBELN', 'NETWR', 'POSNR']  # VBELN: 114... NETWR不含稅金額 POSNR項目編號
    table3 = 'VBAP'
    where3 = ['VBELN <> 0 AND WERKS = \'J150\'']
    results3, headers3 = s_vbap.qry(fields3, table3, where3, maxrows, fromrow)
    '''
    results_df = pd.DataFrame(results, columns=['VBELN', 'WERKS', 'MATNR', 'ERDAT', 'LFIMG', 'VGBEL', 'VGPOS'])
    results2_df = pd.DataFrame(results2, columns=['VBELN', 'KUNNR'])
    results3_df = pd.DataFrame(results3, columns=['VBELN', 'NETWR', 'POSNR'])
    '''
    # print(results_df.sample(10))
    # print(results2_df.sample(10))
    # print(results3_df.sample(10))
    # print(headers)
    # print(headers2)
    # logging.debug('------results (LIPS)-------')
    # pp.pprint(results)
    # logging.debug(results)
    # print(type(results))
    # logging.debug('------results2 (VBAK)-------')
    # pp.pprint(results2)
    # logging.debug(results2)
    logging.debug('**********出貨給怡仁(VBAK-KUNNR)的交貨單(LIPS)*********')
    new_list = []  # 要入到excel做統計處理的list
    # print(type(results))
    # print(len(results2))

    for i in range(len(results)):  # 篩選出買方為怡仁的單據
        for j in range(len(results2)):
            if results[i][5] == results2[j][0]:
                # logging.debug(results[i])
                # logging.debug(results2[j])
                results[i][4] = float((results[i][4]).strip())
                results[i][2] = results[i][2].strip()
                new_list.append(results[i])  # LIPS ['VBELN', 'WERKS', 'MATNR', 'ERDAT', 'LFIMG', 'VGBEL', 'VGPOS', 'ARKTX']

    for k in range(len(new_list)):  # 用出貨單號和項次編號找到未稅金額(NETWR)，加入new_list的每個item的最末項
        for m in range(len(results3)):
            if new_list[k][5] == results3[m][0] and new_list[k][6] == results3[m][2]:  # VBELN114...出貨單號, POSNR項次編號| VBAP: ['VBELN', 'NETWR', 'POSNR']
                new_list[k].append(results3[m][1].strip())
                # logging.debug('--------------new_list-------------')
                # logging.debug(new_list)

                # p[results[i][0]] = results3[k][2]
                # price_list.append(float(results3[k][1])*100)

    return new_list
# print(len(price_list))
# print(p)
# price_list = price_list * 1.05
# print('results3: ', len(results3))  # 7366
# print('save_list: ', len(save_list))  # 6464
# print('results: ', len(results))  # 7235

def to_dataframe():
    # print('GETDATE: \n', getData()) #return the new_list
    start = time.time()
    merged_df = pd.DataFrame(getData(), columns=['shipment_no', 'factory', 'item', 'date', 'quantity', 'Customer_ref_po', 'no', 'description', 'prix_sans_tax']) #二維陣列
    end = time.time()
    trimmed_df = merged_df[['date', 'item', 'description', 'quantity', 'prix_sans_tax', 'shipment_no']]
    # print(trimmed_df.sample(10))
    print('use time (get_data_from_sap):' + str(end - start))
    return trimmed_df  # 我們要做圖、做分析的數據


# to_dataframe()
print('dataframe built!')