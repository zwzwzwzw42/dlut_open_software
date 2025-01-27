# [file name]: KafkaCommitAnalysis.py
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import re
from collections import defaultdict
import os

# ======================
# 数据解析模块
# ======================
def parse_commit_data(input_file):
    """解析Kafka提交记录文件"""
    # 初始化数据结构
    commits = []
    current_commit = {}
    
    # 定义正则模式
    patterns = {
        'commit': re.compile(r'^Commit:\s+(.+)$'),
        'author': re.compile(r'^Author:\s+(.+)$'),
        'date': re.compile(r'^Date:\s+(.+)$'),
        'message': re.compile(r'^Message:\s+(.+)$'),
        'files': re.compile(r'^Changed files:\s+(.+)$')
    }

    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                if current_commit:
                    commits.append(current_commit)
                    current_commit = {}
                continue
                
            for key, pattern in patterns.items():
                match = pattern.match(line)
                if match:
                    current_commit[key] = match.group(1)
                    break
                    
    return pd.DataFrame(commits)

# ======================
# 数据分析模块
# ======================
def analyze_commit_types(messages):
    """分析提交类型分布"""
    type_patterns = {
        'feature': re.compile(r'\b(feat|feature|add)\b', re.I),
        'fix': re.compile(r'\bfix\b', re.I),
        'docs': re.compile(r'\b(docs|documentation)\b', re.I),
        'perf': re.compile(r'\b(perf|optimize)\b', re.I),
        'refactor': re.compile(r'\brefactor\b', re.I)
    }
    
    type_counts = defaultdict(int)
    for msg in messages:
        for t, p in type_patterns.items():
            if p.search(msg):
                type_counts[t] += 1
                break
        else:
            type_counts['other'] += 1
    return type_counts

# ======================
# 可视化模块
# ======================
def plot_treemap(df):
    """生成提交类型树状图"""
    fig = px.treemap(
        df,
        path=[px.Constant("All Commits"), 'author', 'main_module'],
        values='count',
        color='commit_type',
        hover_data=['message_sample'],
        color_continuous_scale='Blues',
        title="Kafka Commit Distribution by Author and Module"
    )
    fig.update_layout(margin=dict(l=20, r=20, t=60, b=20))
    return fig

def plot_commit_activity(df):
    """绘制提交活动时间趋势图（需要日期数据）"""
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)
        monthly = df.resample('M').size()
        
        plt.figure(figsize=(12, 6))
        monthly.plot(kind='line', marker='o')
        plt.title('Monthly Commit Activity')
        plt.ylabel('Number of Commits')
        plt.grid(True)
        plt.tight_layout()
        plt.show()

# ======================
# 主执行流程
# ======================
if __name__ == "__main__":
    # 配置参数
    input_file = "kafka_commits.txt"
    output_dir = "visualizations"
    os.makedirs(output_dir, exist_ok=True)

    # 数据解析
    print("正在解析提交数据...")
    df = parse_commit_data(input_file)
    
    # 数据增强
    print("进行数据分析...")
    # 提取主模块
    df['main_module'] = df['files'].str.split('/').str[0].fillna('unknown')
    
    # 分析提交类型
    type_counts = analyze_commit_types(df['message'])
    type_df = pd.DataFrame({
        'Type': list(type_counts.keys()),
        'Count': list(type_counts.values())
    })
    
    # 作者统计
    author_stats = df['author'].value_counts().reset_index()
    author_stats.columns = ['author', 'count']
    
    # 模块统计
    module_stats = df['main_module'].value_counts().reset_index()
    module_stats.columns = ['module', 'count']

    # ======================
    # 生成可视化
    # ======================
    print("生成可视化图表...")
    
    # 1. 提交类型分布（饼图）
    plt.figure(figsize=(10, 10))
    plt.pie(type_df['Count'], labels=type_df['Type'], autopct='%1.1f%%')
    plt.title("Commit Type Distribution")
    plt.savefig(os.path.join(output_dir, "commit_types_pie.png"))
    
    # 2. 作者提交排名（柱状图）
    plt.figure(figsize=(12, 8))
    sns.barplot(x='count', y='author', data=author_stats.head(15), palette='viridis')
    plt.title("Top 15 Contributors")
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "top_authors.png"))
    
    # 3. 模块热度图（树状图）
    fig = plot_treemap(df)
    fig.write_html(os.path.join(output_dir, "module_treemap.html"))
    
    # 4. 时间趋势图（如果存在日期字段）
    if 'date' in df.columns:
        plot_commit_activity(df)
        plt.savefig(os.path.join(output_dir, "commit_activity.png"))

    print(f"可视化结果已保存至 {output_dir} 目录")