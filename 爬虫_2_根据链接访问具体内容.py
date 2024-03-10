from DrissionPage import ChromiumPage
from DataRecorder import Recorder
from tqdm import tqdm
import time
import random
from datetime import datetime, date
import winsound
import pandas as pd


def sign_in():
    sign_in_page = ChromiumPage()
    sign_in_page.get('https://www.xiaohongshu.com')
    print("请扫码登录")
    # 第一次运行需要扫码登录
    time.sleep(30)


def open_url(url):
    global page
    page = ChromiumPage()
    # page.set.load_mode.eager()
    page.get(f'{url}')


def get_author_info(page):
    # 定位作者信息
    div_author = page.ele('.author-container', timeout=0)
    div_info = div_author.ele('.info', timeout=0)
    # 作者名字
    author_name = div_info.ele('.username', timeout=0).text
    # 作者主页链接
    author_link = div_info.eles('tag:a', timeout=0)[0].link

    author_info = {'author_name': author_name, 'author_link': author_link}
    # print(author_info)
    return author_info


def get_note_content(page):
    # 定位包含笔记详情的div
    note_content = page.ele('.note-content', timeout=0)
    # 标题
    try:
        note_title = note_content.ele('.title', timeout=0).text
    except:
        note_title = ""
        pass
    # 描述
    note_desc = note_content.ele('.desc', timeout=0).text
    try:
        note_desc = note_desc.replace("\n话题可以点击搜索啦~\n", " ")
        # note_desc = note_desc.replace("话题可以点击搜索啦~", " ")
    except:
        pass

    # 发布日期和ip地区
    note_date = note_content.ele('.bottom-container', timeout=0).text

    # 提取日期和ip地区
    note_date_location = {}
    try:
        parts = note_date.split(" ")
        date = parts[0]
        location = parts[1]
        note_date_location['date'] = f"{date}"
        note_date_location['location'] = f"{location}"
    except:
        date = note_date
        location = ""
        note_date_location['date'] = f"{date}"
        note_date_location['location'] = f"{location}"

    # 提取标签
    note_tags = note_content.eles('.tag tag-search', timeout=0)

    # # 每个标签单独占一个单元格
    # tags = {}
    # for tag in note_tags:
    #     tag_id = note_tags.index(tag) + 1
    #     tag_id = f"tag{tag_id}"
    #     tag_text = tag.texts()[0]
    #     tags[f"{tag_id}"] = f"{tag_text}"

    # 所有标签占一个单元格
    tags = []
    for tag in note_tags:
        # tag_id = note_tags.index(tag) + 1
        tag_text = tag.texts()[0]
        tags.append(tag_text)
    # content = {"note_title": note_title, "note_desc": note_desc, "tags": tags,
    #            "tags": tags, "note_date_location": note_date_location}
    content = {'note_title': note_title, 'note_desc': note_desc,
               'tags': tags, 'note_date_location': note_date_location}
    # print(content)
    return content


# 处理以w k + 结尾字符
def parse_count(value):
    if isinstance(value, int):
        return value
    if value.endswith("w"):
        return int(float(value[:-1]) * 10000)
    if value.endswith("w+"):
        return int(float(value[:-2]) * 10000)
    if value.endswith("k"):
        return int(float(value[:-1]) * 1000)
    if value.endswith("k+"):
        return int(float(value[:-2]) * 1000)
    if value.endswith("+"):
        return int(value[:-1])
    return int(value)


def get_count(page):
    # 定位包含点赞、收藏、评论数量信息的div
    div_interactions = page.ele('.interactions engage-bar', timeout=0)
    div_container = div_interactions.ele('.interact-container', timeout=0)
    # 点赞数
    like = div_container.ele('.like-wrapper like-active', timeout=0)
    like_count = like.ele('.count', timeout=0).text
    # 收藏数
    collect = div_container.ele('.collect-wrapper', timeout=0)
    collect_count = collect.ele('.count', timeout=0).text
    # 评论数
    chat = div_container.ele('.chat-wrapper', timeout=0)
    chat_count = chat.ele('.count', timeout=0).text

    count = {'like_count': like_count, 'collect_count': collect_count, 'chat_count': chat_count}
    # 处理以w k + 结尾字符
    count = {key: parse_count(value) for key, value in count.items()}
    # print(count)
    return count


def countdown(n):
    for i in range(n, 0, -1):
        print(f'\r倒计时{i}秒采集下一条笔记详情', end='')  # \r让光标回到行首 ，end=''--结束符为空，即不换行
        time.sleep(1)  # 让程序等待1秒
    else:
        print('\r倒计时结束')


def get_note_page_info(url):
    # 访问url
    open_url(url)
    # 提取作者信息
    author_info = get_author_info(page)
    # 提取笔记内容
    content = get_note_content(page)
    # 提取点赞、收藏、评论数
    count = get_count(page)
    note_contents = {'note_link': url, 'author_info': author_info, 'content': content, 'count': count}

    # 提取信息
    note_title = note_contents['content']['note_title']
    note_link = note_contents['note_link']
    author_name = note_contents['author_info']['author_name']
    author_link = note_contents['author_info']['author_link']
    note_desc = note_contents['content']['note_desc']
    tags = note_contents['content']['tags']
    date = note_contents['content']['note_date_location']['date']
    location = note_contents['content']['note_date_location']['location']
    like_count = note_contents['count']['like_count']
    collect_count = note_contents['count']['collect_count']
    chat_count = note_contents['count']['chat_count']

    # 将字符串转换为日期格式
    date = datetime.strptime(date, "%Y-%m-%d").date()
    # print(date)
    # print(type(date))

    print(f"【笔记标题】{note_title}\n",
          f"【笔记链接】{note_link}\n",
          f"【作者】{author_name}\n",
          f"【作者链接】{author_link}\n",
          # 笔记内容太多，可以不输出显示
          # f"【笔记内容】{note_desc}\n",
          f"【标签】{tags}\n",
          f"【发布日期】{date}\n",
          f"【IP属地】{location}\n",
          f"【点赞数】{like_count}\n",
          f"【收藏数】{collect_count}\n",
          f"【评论数】{chat_count}\n"
          )

    # 数据写入excel

    new_note_contents_dict = {'采集日期': current_date, '作者': author_name, '笔记标题': note_title,
                              '发布日期': date, 'IP属地': location, '点赞数': like_count,
                              '收藏数': collect_count, '评论数': chat_count, '笔记链接': note_link,
                              '作者链接': author_link, '标签': tags, '笔记内容': note_desc}
    r.add_data(new_note_contents_dict)
    # print(r.data)

    # 暂停一个随机时间
    random_time = random.uniform(2, 4)
    random_time = round(random_time, 2)
    time.sleep(random_time)
    print(f"暂停{random_time}秒")

    return note_contents


def read_urls_from_txt(path):
    df = pd.read_excel(path)
    # 提取指定列的数据
    urls = df["笔记链接"].tolist()
    return urls


if __name__ == '__main__':
    # 第1次运行需要登录，后面不用登录，可以注释掉
    # sign_in()

    # 获取当前时间
    current_time = time.localtime()
    # 格式化当前时间
    formatted_time = time.strftime("%Y-%m-%d %H%M%S", current_time)

    # 新建一个excel表格，用来保存数据
    r = Recorder(path=f'采集输出-小红书笔记详情{formatted_time}.xlsx', cache_size=1)

    # 获取当前日期
    current_date = date.today()

    # 设置要采集的笔记链接
    # 多篇小红书笔记的url地址放在txt文件里，每行放1个url
    note_urls_file_path = 'F:/小红书-LZC/小红书搜索结果-综合-图文-婚姻-108条.xlsx'

    # 从txt文件读取urls
    note_urls = read_urls_from_txt(note_urls_file_path)

    # 异常情况的笔记链接放到error_url列表里，方便程序运行结束后排查
    error_url = []
    for note_url in tqdm(note_urls):
        # 采集笔记详情，返回一个note_contents字典
        try:
            note_contents = get_note_page_info(note_url)
        except:
            print(f"请处理验证码，或检查网址是否失效。当前网址是:  {note_url}")
            error_url.append(note_url)
            print(f"截止目前有{len(error_url)}个异常网址，所有异常网址如下，请在程序运行结束后排查。{error_url}")

            # 把发生错误的链接存到txt文件
            # 将列表中的元素转换为字符串格式
            error_url_str = '\n'.join(error_url)
            # 打开一个文件，并将字符串写入到文件中
            file1 = open(f'error_url-{formatted_time}.txt', 'w')
            file1.write(error_url_str)
            file1.close()
            print(f'异常笔记链接已保存到文件：error_url-{formatted_time}.txt')

            # 发出声音报警
            duration = 3000  # 声音持续时间，单位为毫秒
            freq = 440  # 声音频率，单位为赫兹
            winsound.Beep(freq, duration)
            # 倒计时60s
            countdown(60)

            continue

        # 将note_contents字典转换为字符串
        # note_contents = json.dumps(note_contents, separators=(',', ':'), ensure_ascii=False)
        # print(type(note_contents), "笔记详情：", note_contents)

    # 保存excel文件
    r.record()

