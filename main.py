import sys
import argparse
import asyncio

sys.path.append("scrape")
sys.path.append("tests")

from scrape import extract_data, scrape_util
from tests import union_based, boolean_based, time_based

class SQLInjectionTester:
    def __init__(self):
        self.parser = argparse.ArgumentParser(description="Program pengujian kerentanan SQL Injection pada situs web.")
        self.setup_arguments()

    def setup_arguments(self):
        self.parser.add_argument("url", help="Alamat URL situs web yang akan diuji.")
        self.parser.add_argument("-a", "--all", help="Pengujian secara menyeluruh", action="store_true")
        self.parser.add_argument("-s", "--single", metavar="Type", choices=["boolean", "union", "time"], help="Pengujian berdasarkan jenis")
        self.parser.add_argument("-o", "--output", metavar="report.txt", help="Target keluaran report")
        
    def run_tests(self):
        args = self.parser.parse_args()

        if args.all:
            self.run_comprehensive_test(args.url, args.output)
        elif args.single:
            self.run_single_test(args.url, args.single, args.output)
        else:
            print("Contoh: python program.py -s boolean 'http://localhost' -o reports.txt")

    def run_comprehensive_test(self, url, output):
        print(f"Pengujian semua jenis pada {url} dengan keluaran report: {output}\n")
        
        results = []
        try:
            result_scrape = extract_data.do_request(url)
            scrape_util.save_url(result_scrape, 'result/result-scrape.txt')
        except:
            print("[!] Terjadi kesalahan saat terhubung dengan host!")
            return
        
        result_boolean = boolean_based.do_test()
        results += result_boolean
        result_union = union_based.do_test()
        results += result_union
        result_time = asyncio.run(time_based.do_test())
        results += result_time

        scrape_util.save_report(url, "Boolean, Time Based, Union Based", output, results)

    def run_single_test(self, url, test_type, output="report.txt"):
        results = []
        print(f"\nPengujian single jenis {test_type} pada {url} dengan keluaran report: {output}\n")
        
        try:
            result_scrape = extract_data.do_request(url)
            scrape_util.save_url(result_scrape, 'result/result-scrape.txt')
        except:
            print("[!] Terjadi kesalahan saat terhubung dengan host!")
            return
        
        if (test_type == "boolean"):
            result_boolean = boolean_based.do_test()
            results += result_boolean
        elif (test_type == "union"):
            result_union = union_based.do_test()
            results += result_union
        elif (test_type == "time"):
            result_time = asyncio.run(time_based.do_test())
            results += result_time

        scrape_util.save_report(url, test_type, output, results)
    
    def custom_error(self, message):
        print(f"error: {message}\n\nGunakan argumen -h untuk membaca dokumentasi.")
    
    def custom_help(self):
        return ("""
Deskripsi:
    Program pengujian kerentanan SQL Injection pada situs web.
                
Penggunaan:
    python program.py [opsi] [alamat_url] -o [report_keluaran]
        
Opsi:
    -a, --all                               Pengujian seluruh jenis
    -p, --plugin                            Pengujian dengan memindai plugin
    -s Type, --single=Type                  Pengujian berdasarkan jenis
    -o report.txt, --output=report.txt      Target keluaran report   

Type:
    boolean                                 Pengujian Boolean-Based SQL Injection
    union                                   Pengujian Union-Based SQL Injection
    time                                    Pengujian Time-Based SQL Injection

Contoh:
    python program.py -s boolean "http://localhost" -o report.txt               
                """
        )

if __name__ == "__main__":
    tester = SQLInjectionTester()
    tester.parser.format_help = tester.custom_help
    tester.parser.error = tester.custom_error
    tester.run_tests()

