import pandas as pd
import subprocess
from concurrent.futures import ThreadPoolExecutor

def test_ip(ip_port):
    try:
        ip, port = ip_port.split(':')
        # 测试连通性（3秒超时）
        speed = 100 if subprocess.call(
            f"nc -z -w3 {ip} {port} >/dev/null 2>&1",
            shell=True
        ) == 0 else 0
        return (ip_port, speed)
    except:
        return (ip_port, 0)

if __name__ == "__main__":
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    df = pd.read_csv(input_file, header=None, names=['ip_port'])
    with ThreadPoolExecutor(max_workers=20) as executor:
        results = list(executor.map(test_ip, df['ip_port']))
    
    # 保存带评分的原始数据
    df = pd.DataFrame(results, columns=['ip_port', 'score'])
    df.to_csv('score_data.csv', index=False)
    
    # 生成排序后的IP列表
    df.sort_values('score', ascending=False)[['ip_port']].to_csv(output_file, index=False)
