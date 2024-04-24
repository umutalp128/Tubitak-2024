using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.IO;
using System.IO.Ports;
using System.Linq;
using System.Net;
using System.Net.Http;
using System.Net.Mail;
using System.Reflection.Emit;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using System.Windows.Forms;
using System.Xml;
using static System.Windows.Forms.VisualStyles.VisualStyleElement;
namespace telefonAlgila
{
    public partial class Form1 : Form
    {
        //değişken ve nesneleri tanımla
        static SerialPort serialPort;
        static String path;
        static bool durum = false;
        static char cdurum = 'n';
        static String arac = "test";
        static string portName = "COM4";
        static int baudRate = 115200;
        static DataTable dtbl = new DataTable();
        static RichTextBox tablo;
        static SaveFileDialog saveFileDialog;
        public Form1()
        {
            serialPort = new SerialPort(portName, baudRate);
            InitializeComponent();
            string userdir = Environment.GetFolderPath(Environment.SpecialFolder.UserProfile);
            //o anki zamana göre log klasörünü oluştur
            string filename = string.Format("{0:yyyy_MM_dd_HH_mm_ss}.log", DateTime.Now);
            Directory.CreateDirectory(userdir + @"\Desktop\logs");
            path = userdir + @"\Desktop\logs\" + filename;
            //Console.WriteLine(path);
            //tabloyu ayarla
            tablo = richTextBox1;
            dtbl.Columns.Add("Araç", typeof(string));
            dtbl.Columns.Add("Tespit Sayisi", typeof(int));
            dtbl.Rows.Add("Test Odasi 1", 0);
            tablo.Rtf = InsertTableInRichTextBox(dtbl);
            //dosya kayıt nesnesini ayarla
            saveFileDialog = saveFileDialog1;
            
        }
        private static void SerialPort_DataReceived(object sender, SerialDataReceivedEventArgs e)
        {
            //portu oku
            string v = serialPort.ReadLine();
            string receivedMessage = v;
            //gelen mesajı decode et
            arac = receivedMessage.Remove(receivedMessage.IndexOf('$'));
            cdurum = receivedMessage.ElementAt(receivedMessage.IndexOf('$') + 1);
            if (cdurum == 'y')
            {
                //durum evet ise
                durum = true;
                addToTable();
                Console.WriteLine("algilandi");
            }
            else if (cdurum == 'n')
            {
                //durum hayır ise
                durum = false;
            }
            //Console.WriteLine(durum);
           // Console.WriteLine(arac);
           //log dosyasına ekle
            File.AppendAllText(path,receivedMessage);
        }
      
        private void Form1_Load(object sender, EventArgs e)
        {
            Control.CheckForIllegalCrossThreadCalls = false;
            //port isimlerini al ve foreach döngüsü ile göster
            string[] ports = SerialPort.GetPortNames(); 
            foreach (string port in ports)
            {
               portSelector.Items.Add(port);
            }
           
        }
        //84-136.satırlar https://www.dotnetstuffs.com/create-table-in-richtextbox-using-c-sharp/ 'dan alınmıştır
        private static String InsertTableInRichTextBox(DataTable dtbl)
        {

            StringBuilder sringTableRtf = new StringBuilder();

            sringTableRtf.Append(@"{\rtf1");

           
            sringTableRtf.Append(@"\trowd");

           
            for (int j = 0; j < dtbl.Columns.Count; j++)
            {
               
                sringTableRtf.Append(@"\fs20");

                if (j == 0)
                {
                    sringTableRtf.Append(@"\intbl  " + dtbl.Columns[j].ColumnName);
                }
                else
                {
                    sringTableRtf.Append(@"\cell   " + dtbl.Columns[j].ColumnName);
                }
                
            }

            
            sringTableRtf.Append(@"\intbl \cell \row");

            for (int i = 0; i < dtbl.Rows.Count; i++)
            {

                sringTableRtf.Append(@"\trowd");

                for (int j = 0; j < dtbl.Columns.Count; j++)
                {

                  sringTableRtf.Append(@"\fs20");

                    if (j == 0)
                        sringTableRtf.Append(@"\intbl  " + dtbl.Rows[i][j].ToString());
                    else
                        sringTableRtf.Append(@"\cell   " + dtbl.Rows[i][j].ToString());
                }

                sringTableRtf.Append(@"\intbl \cell \row");
            }

            sringTableRtf.Append(@"\pard");
            sringTableRtf.Append(@"}");
            return sringTableRtf.ToString();
        }
        public static void SendMail(string arac,int tespit)
        {
            //mesaj sttringini tanımla
            string mesaj;
            //mesaj stringine gerekli bilgileri ekle
            mesaj = @"'" + arac + @"' isimli araçta, " + tespit + " kez telefon tespit edildi" ;
            MailMessage eMail = new MailMessage();
            //gönderilecek email için gerekli bilgileri ekle
            eMail.From = new MailAddress("************");
            eMail.To.Add("***********");
            eMail.Subject = "Telefon Tespit Edildi";
            eMail.Body = mesaj;
            //smtpclient
            SmtpClient smtp1 = new SmtpClient();
            //smtp için gerekli bilgilerini tanımla
            smtp1.Host = "smtp.yandex.com";
            smtp1.Port = 587;
            smtp1.UseDefaultCredentials = false;
            // TODO: özel bilgileri çıkart
            smtp1.Credentials = new NetworkCredential("**********", "***********");
            smtp1.EnableSsl = true;
            //email'i gönder
            smtp1.Send(eMail);
        }
        private void open_Click(object sender, EventArgs e)
        {
            serialPort.DataReceived += SerialPort_DataReceived;
            serialPort.ReadTimeout = 30000; 
            //portu aç
            serialPort.Open();
        }
        public static void addToTable()
        {
            //richtextbox'taki tobloya veri elemek\düzenlemek için
            DataRow row = dtbl.Rows[0];
            row[1] = (int)row[1] + 1;
            tablo.Rtf = InsertTableInRichTextBox(dtbl);
            //veri eklendi ise telefon tespit edilmiştir , bu sebepten dolayı mail gönder 
            //SendMail("Test Odasi 1", (int)row[1]);
            Thread.Sleep(2500);
        }

        private void close_Click(object sender, EventArgs e)
        {
            // portu kapat
            serialPort.Close();

        }

        private void portSelector_SelectedIndexChanged(object sender, EventArgs e)
        {
            serialPort.PortName = portSelector.SelectedItem.ToString(); //port seçici
        }

        private void richTextBox1_TextChanged(object sender, EventArgs e)
        {

        }

        private void save_Click(object sender, EventArgs e)
        {
            //kaydet arayzünü ayarla
            saveFileDialog.Filter = @"Zengin Metin Biçimi (*.rtf)|*.rtf|Tüm dosyalar (*.*)|*.*";
            saveFileDialog.CheckPathExists = true; 
            //saveFileDialog.CheckFileExists = true;   
            //kaydet arayüzünü göster
            saveFileDialog.ShowDialog();
        }

        private void saveFileDialog1_FileOk(object sender, CancelEventArgs e)
        {
            //kaydet arayüzünde kaydete basıldığında kaydet
            File.WriteAllText(saveFileDialog1.FileName,tablo.Rtf);
        }
        
    }
}
