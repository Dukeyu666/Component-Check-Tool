from configparser import ConfigParser
import pyodbc,setting

class Dbconnect:
    def __init__(self,server):
        config=ConfigParser()
        config.read_string(setting.value)
        self.server=config[server]['server']
        self.database=config[server]['database']
        self.username=config[server]['username']
        self.password=config[server]['password']
    def connector(self): 
        self.cnxn = pyodbc.connect(\
        'DRIVER={SQL Server Native Client 11.0};SERVER='+self.server+';DATABASE=' +self.database+\
        ';UID='+self.username+';PWD='+ self.password,timeout=6)
        return self.cnxn
    
    def ready_chk(self,component):
        """
        string=\
        "declare @Component varchar(14)='"+component+"',@existed varchar(15)=null; "+\
        "select top 1 @existed=SkuNumber from sku "+\
        "where SkuNumber=@Component order by Revision desc; "+\
        """
        """
        if(@existed is not null)
         begin
             select Sku.SkuNumber,sku.Revision,skuok.InsertedTime from SKU
             inner join SkuOK on sku.SkuKey=skuok.SkuKey  
             where sku.SkuNumber =@Component and 
             sku.Revision =(select MAX(Revision) from sku where sku.SkuNumber=@Component);
         end
        else
         begin
          select @Component+' not exist in the server.' as result ;
         end"""

        string=\
            "declare @Component varchar(14)='"+component+"',@ReadyTime datetime,@EOL datetime; "+\
            "select @EOL=EndofLife from SKU where SkuNumber=@Component; "+\
            """select @ReadyTime=skuok.InsertedTime from SKU
                inner join SkuOK on sku.SkuKey=skuok.SkuKey  
                where sku.SkuNumber =@Component and 
                sku.Revision =(select MAX(Revision) from sku where sku.SkuNumber=@Component); """+\
            """if(@EOL >= GETDATE())
                 begin
	              select Sku.SkuNumber,sku.Revision,skuok.InsertedTime,sku.EndofLife from SKU
 	              inner join SkuOK on sku.SkuKey=skuok.SkuKey  
                  where sku.SkuNumber =@Component and 
                  sku.Revision =(select MAX(Revision) from sku where sku.SkuNumber=@Component)
                  end
                else
                 begin
                  if(@EOL is not null)   
	               select 'EOL';
                  else
                   select @Component+' not exist in the server.';
                 end"""       
  
        result=self.cnxn.cursor().execute(string).fetchone()
        self.cnxn.close()
        return result
    
    def ML_chk(self,component):
        string="exec spcheckML "+component
        cursor=self.cnxn.cursor()
        cursor.execute(string)
        record=[]
        if cursor.nextset():
            results=cursor.fetchall()
            for result in results:
                record.append([result[0].strip(),result[2].replace(result[0],"").strip()])
        else:
            record=None
        cursor.close()
        return record
    def PML_chk(self,components_list: list):
        def sql_string(sku):
            string=\
            "declare @Component varchar(14)='"+sku+"',@ReadyTime datetime,@EOL datetime; "+\
            "select @EOL=EndofLife from SKU where SkuNumber=@Component; "+\
            """select @ReadyTime=skuok.InsertedTime from SKU
                inner join SkuOK on sku.SkuKey=skuok.SkuKey  
                where sku.SkuNumber =@Component and 
                sku.Revision =(select MAX(Revision) from sku where sku.SkuNumber=@Component); """+\
            """if(@EOL >= GETDATE())
                 begin
                    if(@ReadyTime is not null)
	                    begin
                        select Sku.SkuNumber,sku.Revision,skuok.InsertedTime,sku.EndofLife from SKU
 	                    inner join SkuOK on sku.SkuKey=skuok.SkuKey  
                        where sku.SkuNumber =@Component and 
                        sku.Revision =(select MAX(Revision) from sku where sku.SkuNumber=@Component)
                        end
                    else
                        select @Component,'Syncronizing';
                 end
                else
                 begin
                  if(@EOL is not null)   
	               select @Component,'EOL';
                  else
                   select @Component,'Not exist';
                 end"""
            return string
        result=[]
        for li in components_list:
            fetch=self.cnxn.cursor().execute(sql_string(li)).fetchone()
            result.append(fetch)
        self.cnxn.close()
        return result


