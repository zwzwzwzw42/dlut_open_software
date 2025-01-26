from collections import defaultdict
import csv
import re

def parse_kafka_commits():
    categories = defaultdict(int)
    file_path = 'kafka_info.txt'  # Kafka提交记录文件路径

    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
        # 使用更通用的分割方式（Linux示例中的分隔符）
        commits = content.split('-------------------------------------------')
        
        for commit in commits:
            if not commit.strip():
                continue

            lines = commit.strip().split('\n')
            message = ""
            
            # 提取提交消息
            for line in lines:
                if line.startswith('Message:'):
                    message = line[len('Message:'):].strip()
                    break
            
            if not message:
                continue

            # 处理Kafka特定的提交模式
            # 1. 处理合并请求（GitHub风格）
            if message.startswith('Merge pull request'):
                pr_match = re.search(r'#\d+', message)
                if pr_match:
                    categories["Merge pull requests"] += 1
                else:
                    categories["Merge commits"] += 1
            
            # 2. 处理KAFKA issue编号（如KAFKA-1234）
            elif 'KAFKA-' in message:
                parts = message.split(':', 1)
                if len(parts) > 1:
                    category = parts[0].strip()
                    categories[category] += 1
                else:
                    categories["KAFKA Issues"] += 1
            
            # 3. 处理模块前缀（如 core:）
            elif ':' in message:
                parts = message.split(':', 1)
                category = parts[0].strip()
                categories[category] += 1
            
            # 4. 其他情况归类为Misc
            else:
                categories["Misc"] += 1

    return dict(categories)

def write_to_csv(categories_count, output_file='kafka_category_counts.csv'):
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Category', 'Count'])
        for category, count in sorted(categories_count.items(), key=lambda x: -x[1]):
            writer.writerow([category, count])

if __name__ == "__main__":
    categories = parse_kafka_commits()
    write_to_csv(categories)
    print("CSV文件已生成：kafka_category_counts.csv")