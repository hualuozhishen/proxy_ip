def generate_rating(score):
    rating_map = {
        (90, 100): "★★★★★",
        (80, 89): "★★★★☆",
        (70, 79): "★★★☆☆",
        (60, 69): "★★☆☆☆",
        (0, 59): "★☆☆☆☆"
    }
    for (low, high), stars in rating_map.items():
        if low <= score <= high:
            return stars
    return "★☆☆☆☆"

def create_report(input_file, output_file):
    with open(input_file, 'r') as f:
        ips = [line.strip() for line in f if line.strip()]
    
    ranked = []
    for ip in ips:
        # 提取分数（假设格式为 ip:port@score）
        parts = ip.split('@')
        if len(parts) == 2:
            score = int(parts[1])
            stars = generate_rating(score)
            ranked.append(f"{stars} {parts[0]}")
    
    with open(output_file, 'w') as f:
        f.write('\n'.join(ranked))

if __name__ == "__main__":
    import sys
    create_report(sys.argv[1], sys.argv[2])
