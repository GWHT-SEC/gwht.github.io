import os
import hashlib
import pandas as pd
from shutil import copyfile

class MemberProcessor:
    def __init__(self):
        # 初始化MD5哈希生成函数
        self.get_md5 = lambda text: hashlib.md5(str(text).encode('utf-8')).hexdigest()
        
    def process_avatars(self, csv_path, attachments_dir, output_dir="static\\memberpic"):
        """处理头像图片，按个人ID的MD5重命名并保存"""
        # 创建输出文件夹
        os.makedirs(output_dir, exist_ok=True)
        print(f"图片将保存到：{os.path.abspath(output_dir)}")
        
        # 读取CSV数据
        df = pd.read_csv(csv_path)
        
        # 检查必要的列
        if '编号' not in df.columns or '个人ID' not in df.columns:
            raise ValueError("CSV文件中缺少必要的'编号'或'个人ID'列")
        
        # 处理每个成员的头像
        for _, row in df.iterrows():
            try:
                file_id = str(int(row['编号']))
                person_id = row['个人ID']
                
                # 查找对应编号的图片
                image_extensions = ['jpg', 'jpeg', 'png']
                source_path = None
                for ext in image_extensions:
                    candidate = os.path.join(attachments_dir, f"{file_id}.{ext}")
                    if os.path.exists(candidate):
                        source_path = candidate
                        break
                
                if not source_path:
                    print(f"⚠️ 未找到图片：编号{file_id}（对应ID：{person_id}）")
                    continue
                
                # 计算目标文件名
                md5_name = self.get_md5(person_id)
                _, ext = os.path.splitext(source_path)
                target_path = os.path.join(output_dir, f"{md5_name}{ext}")
                
                # 复制图片
                copyfile(source_path, target_path)
                print(f"✅ 处理成功：{os.path.basename(source_path)} -> {md5_name}{ext}")
                
            except Exception as e:
                print(f"❌ 处理失败（编号{row['编号']}，ID：{row['个人ID']}）：{str(e)}")
        
        return output_dir
    
    def generate_yaml(self, csv_path, output_yaml="members.yaml"):
        """生成成员信息YAML文件"""
        # 读取CSV数据
        df = pd.read_csv(csv_path)
        
        # 确保必要的列存在
        required_columns = ['入学年限 2', '个人ID', '博客地址', '个人简介', '提交人', '编号']
        for col in required_columns:
            if col not in df.columns:
                raise ValueError(f"CSV文件中缺少必要的列: {col}")
        
        # 按入学年限排序
        df['入学年份'] = df['入学年限 2'].str.extract('(\d+)').astype(float)
        df = df.sort_values('入学年份', ascending=False)
        
        # 生成YAML内容
        yaml_content = []
        current_year = None
        
        for _, row in df.iterrows():
            year = row['入学年限 2']
            
            # 添加年级标题
            if year!= current_year:
                current_year = year
                yaml_content.append(f'- title: 20{current_year}\n')
            
            # 获取头像文件名和扩展名
            avatar_md5 = self.get_md5(row['个人ID'])
            avatar_ext = None
            
            # 查找对应编号的图片扩展名（与图片处理保持一致）
            image_extensions = ['jpg', 'jpeg', 'png']
            for ext in image_extensions:
                candidate = os.path.join(attachments_dir, f"{row['编号']}.{ext}")
                if os.path.exists(candidate):
                    avatar_ext = ext
                    break
            
            # 如果找不到扩展名，默认使用jpg
            if not avatar_ext:
                avatar_ext = 'jpg'
                print(f"⚠️ 无法确定{row['个人ID']}的头像扩展名，使用默认值{avatar_ext}")
            
            # 添加成员信息
            member_info = f'''- name: {row['个人ID']}
  link: {row['博客地址'] if pd.notna(row['博客地址']) else ''}
  description: {row['个人简介'] if pd.notna(row['个人简介']) else ''}
  avatar: "/memberpic/{avatar_md5}.{avatar_ext}"
'''
            yaml_content.append(member_info)
        
        # 保存到YAML文件
        with open(output_yaml, 'w', encoding='utf-8') as f:
            f.write('\n'.join(yaml_content).strip())
        
        print(f"YAML文件已生成: {os.path.abspath(output_yaml)}")
        return output_yaml

if __name__ == "__main__":
    # 文件路径配置
    csv_path = r"实验室成员信息_实验室成员信息_收集结果.csv"
    attachments_dir = r"实验室成员信息_实验室成员信息_附件"
    output_yaml = r"data\\links.yaml"
    
    # 创建处理器实例
    processor = MemberProcessor()
    
    # 先处理头像图片
    processor.process_avatars(csv_path, attachments_dir)
    
    # 再生成YAML文件（确保使用相同的MD5逻辑）
    processor.generate_yaml(csv_path, output_yaml)
    
    print("\n处理完成！头像和YAML文件已同步生成")
