import pandas as pd
import subprocess
from concurrent.futures import ThreadPoolExecutor
import argparse

def test_ip(ip_port):
    try:
        ip, port = ip_port.split(':')
        # TCP连接测试
        speed = 100 if subprocess.call(
            f"nc -z -w3 {ip} {port} >/dev/null 2>&1",
            shell=True
        ) == 0 else 0
        return (ip_port, speed)
    except Exception as e:
        logging.error(f"Error testing {ip_port}: {str(e)}")
        return (ip_port, 0)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('input', help='Input raw IP file')
    parser.add_argument('output', help='Output ranked IP file')
    args = parser.parse_args()
    
    df = pd.read_csv(args.input, header=None, names=['ip_port'])
    
    with ThreadPoolExecutor(max_workers=20) as executor:
        results = list(executor.map(test_ip, df['ip_port']))
    
    df = pd.DataFrame(results, columns=['ip_port', 'score'])
    df.to_csv(args.output, index=False)

if __name__ == "__main__":
    main()
