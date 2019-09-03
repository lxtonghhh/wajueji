import smtplib
from email.message import EmailMessage
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage

MAIL_CONFIG = dict(
    # 163邮箱服务器地址
    mail_host='smtp.163.com',
    # 163用户名
    mail_user='liuzeduo1234',
    # 密码(部分邮箱为授权码)
    mail_pass='liuzeduo123,',
)


def mail_init(_from, _to):
    message = MIMEMultipart()
    # 发送方信息
    message['From'] = _from
    # 接受方信息
    message['To'] = _to
    return message


def add_subject(message, title):
    # 邮件主题
    message['Subject'] = title


def load_content(raw_content, filename=None):
    if not filename:
        content = '''
            <html>
                <head></head>
                <body>
                    <p>{0}</p>
                </body>
            </html>
        '''.format(raw_content)

    else:
        with open(filename, 'r') as f:
            c = f.read()
            # 设置html格式参数
            content = MIMEText(c, 'html', 'utf-8')
    #print(content)
    return content


def add_content(massage, content, is_html=True):
    if is_html:
        f = MIMEText(content, 'html', 'utf-8')
    else:
        f = MIMEText(content, 'plain', 'utf-8')
    massage.attach(f)


def add_attachment(massage, filename):
    format = filename.split(".")[1]
    if format in ['jpg', 'png']:
        with open(filename, 'rb')as fp:
            f = MIMEImage(fp.read())
    else:
        with open(filename, 'r')as fp:
            content = fp.read()
        # 设置txt参数
        f = MIMEText(content, 'plain', 'utf-8')
    # 附件设置内容类型，方便起见，设置为二进制流
    f['Content-Type'] = 'application/octet-stream'
    # 设置附件头，添加文件名
    f['Content-Disposition'] = 'attachment;filename="' + filename + '"'
    massage.attach(f)


def send_message(subject, content, content_file=None, attachments=[]):
    # 登录并发送邮件
    sender = 'liuzeduo1234@163.com'
    receivers = ['liuzeduo1234@163.com']
    try:
        smtpObj = smtplib.SMTP()
        # 连接到服务器
        smtpObj.connect(MAIL_CONFIG['mail_host'], 25)
        # 登录到服务器
        smtpObj.login(MAIL_CONFIG['mail_user'], MAIL_CONFIG['mail_pass'])
        for receiver in receivers:
            m = mail_init(_from=sender, _to=receiver)
            add_subject(m, subject)
            add_content(m, content=load_content(raw_content=content, filename=content_file))
            for attachment in attachments:
                add_attachment(m, filename=attachment)

            smtpObj.sendmail(
                sender, receiver, m.as_string())
        # 退出
        smtpObj.quit()
        print('success')
    except smtplib.SMTPException as e:
        print('error', e)  # 打印错误


if __name__ == '__main__':
    send_message(subject="cmh吃粑粑", content="粉红便便", attachments=[])
