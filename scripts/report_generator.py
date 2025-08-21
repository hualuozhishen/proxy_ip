def generate_rating(score):
    stars = {
        90: "★★★★★",
        80: "★★★★☆",
        70: "★★★☆☆",
        60: "★★☆☆☆",
        0: "★☆☆☆☆"
    }
    return stars.get(min(max(int(score),0),90), "★☆☆☆☆")

def create_report(ip_list):
    report = []
    for ip in sorted(ip_list, key=lambda x: x[1], reverse=True):
        stars = generate_rating(ip[1])
        report.append(f"{stars} {ip[0]}")
    return "\n".join(report)

if __name__ == "__main__":
    with open('ranked_ips.txt', 'r') as f:
        ips = [line.strip().split('@') for line in f if line.strip()]
    
    # 读取评分数据
    df = pd.read_csv('score_data.csv', header=None, 
                    names=['ip_port', 'score'])
    
    print(create_report(df.itertuples()))
