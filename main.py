#!/home/robot/.envs/reddit-video/bin/python

import praw
import gtts
import os
from PIL import Image, ImageDraw, ImageFont
import textwrap
import sys
import requests
from io import BytesIO


def read_save(text, filename, reply=False, transition=True):
    tts = gtts.gTTS(text, lang="pt-pt",)
    tts.save("audios/{}_temp.mp3".format(filename))
    if transition:
        os.system(
            'ffmpeg -i audios/{}_temp.mp3 -filter:a "atempo=1.5" -vn -loglevel quiet audios/{}_temp2.mp3 -y'.format(
                filename, filename
            )
        )
        os.system(
            "ffmpeg -i audios/{}_temp2.mp3 -i transition.mp3 -filter_complex [0:a][1:a]concat=n=2:v=0:a=1 -vn -loglevel quiet audios/{}.mp3 -y".format(
                filename, filename
            )
        )
        os.system("rm audios/{}_temp2.mp3".format(filename))
    else:
        os.system(
            'ffmpeg -i audios/{}_temp.mp3 -filter:a "atempo=1.5" -vn -loglevel quiet audios/{}.mp3 -y'.format(
                filename, filename
            )
        )
    os.system("rm audios/{}_temp.mp3".format(filename))
    return int(
        os.popen(
            "ffmpeg -i audios/"
            + filename
            + ".mp3 2>&1 | grep \"Duration\"| cut -d ' ' -f 4 | sed s/,// | sed 's@\..*@@g' | awk '{ split($1, A, \":\"); split(A[3], B, \".\"); print 3600*A[1] + 60*A[2] + B[1] }'"
        ).read()
    )


def intro_img(author, title, description, score):
    font_size = 24
    width = 1920
    font_width = font_size // 1.55
    line_height = int(font_size * 1.5)

    font1 = ImageFont.truetype("/usr/share/fonts/TTF/DejaVuSansMono.ttf", font_size)
    font2 = ImageFont.truetype(
        "/usr/share/fonts/TTF/DejaVuSansMono-Bold.ttf", int(font_size * 1.5)
    )

    lines_title = textwrap.wrap(title, width=(width - 100) // font_width)
    lines_title_nr = len(lines_title) + 1

    lines_description = textwrap.wrap(description, width=(width - 100) // font_width)
    lines_description_nr = len(lines_description)

    image = Image.new(
        mode="RGB",
        size=(
            width,
            lines_title_nr * int(line_height * 1.5)
            + lines_description_nr * line_height
            + 10,
        ),
        color="#1A1A1A",
    )
    draw = ImageDraw.Draw(image)
    draw_header(draw, 10, 16, score, author)

    y = 10 + line_height
    for line in lines_title:
        draw.text((90, y), line, font=font2, fill="#ffffff")
        y += line_height * 1.5

    for line in lines_description:
        draw.text((90, y), line, font=font1, fill="#ffffff")
        y += line_height

    # save file
    image.save("images/000.png")


def draw_header(draw, x, y, score, user):
    font_symbol = ImageFont.truetype(
        "/usr/share/fonts/TTF/DejaVuSansMono-Bold.ttf", 124
    )
    font_score = ImageFont.truetype("/usr/share/fonts/TTF/DejaVuSansMono-Bold.ttf", 22)
    font_text = ImageFont.truetype("/usr/share/fonts/TTF/DejaVuSansMono.ttf", 20)

    draw.text((x, y - 44), "\u2b06", font=font_symbol, fill=(255, 69, 0))
    draw.text((x, y - 4), "\u2b07", font=font_symbol, fill="#818384")
    draw.rectangle([(x - 10, y + 30), (x + 62, y + 70)], fill="#1A1A1A")
    if score >= 10000:
        score_str = "{}K".format(score // 1000)
        draw.text((x + 8, y + 36), score_str, font=font_score, fill=(255, 69, 0))
    if score >= 1000:
        score_str = "{:.1f}K".format(score / 1000)
        draw.text((x + 8, y + 36), score_str, font=font_score, fill=(255, 69, 0))
    else:
        score_str = str(score)
        draw.text((x + 16, y + 36), score_str, font=font_score, fill=(255, 69, 0))
    draw.text(
        (x + 82, y), "Publicado por u/{}".format(user), font=font_text, fill="#818384"
    )


def draw_header_comment(draw, x, y, score, user):
    font_symbol = ImageFont.truetype(
        "/usr/share/fonts/TTF/DejaVuSansMono-Bold.ttf", 124
    )
    font_score = ImageFont.truetype("/usr/share/fonts/TTF/DejaVuSansMono-Bold.ttf", 22)
    font_text = ImageFont.truetype("/usr/share/fonts/TTF/DejaVuSansMono.ttf", 20)

    if score >= 10000:
        score_str = "{}K".format(score // 1000)
    if score >= 1000:
        score_str = "{:.1f}K".format(score / 1000)
    else:
        score_str = str(score)

    draw.text((x, y - 40), "\u2b06", font=font_symbol, fill=(255, 69, 0))
    draw.text((x, y - 8), "\u2b07", font=font_symbol, fill="#818384")
    draw.rectangle([(x - 10, y + 34), (x + 62, y + 64)], fill="#1A1A1A")
    draw.text((x + 80, y), user, font=font_text, fill=(69, 139, 186))
    draw.text(
        (x + 80 + len(user) * 14, y),
        "{} pontos".format(score_str),
        font=font_text,
        fill="#818384",
    )


def post_img(author, text, score, number):
    font_size = 24
    width = 1920
    font_width = font_size // 1.55
    line_height = int(font_size * 1.5)

    font = ImageFont.truetype("/usr/share/fonts/TTF/DejaVuSansMono.ttf", font_size)

    lines = textwrap.wrap(text, width=(width - 100) // font_width)
    lines_nr = len(lines) + 1

    image = Image.new(
        mode="RGB", size=(width, lines_nr * line_height + 30), color="#1A1A1A"
    )
    draw = ImageDraw.Draw(image)
    draw_header_comment(draw, 10, 16, score, author)

    y = 10 + line_height
    for line in lines:
        draw.text((90, y), line, font=font, fill="#ffffff")
        y += line_height

    # save file
    image.save("images/{:03d}_0.png".format(number))


def post_img_reply(
    author, text, score, author_reply, text_reply, score_reply, number, hide=False
):
    font_size = 24
    width = 1920
    font_width = font_size // 1.55
    line_height = int(font_size * 1.5)

    font = ImageFont.truetype("/usr/share/fonts/TTF/DejaVuSansMono.ttf", font_size)

    lines = textwrap.wrap(text, width=(width - 100) // font_width)
    lines_nr = len(lines) + 1

    lines_reply = textwrap.wrap(text_reply, width=(width - 138) // font_width)
    lines_nr_reply = len(lines_reply) + 1

    image = Image.new(
        mode="RGB",
        size=(width, (lines_nr + lines_nr_reply) * line_height + 60),
        color="#1A1A1A",
    )
    draw = ImageDraw.Draw(image)
    draw_header_comment(draw, 10, 16, score, author)

    y = 10 + line_height
    for line in lines:
        draw.text((90, y), line, font=font, fill="#ffffff")
        y += line_height

    if not hide:
        y += 10
        draw_header_comment(draw, 48, y, score_reply, author_reply)
        y += line_height
        for line in lines_reply:
            draw.text((128, y), line, font=font, fill="#ffffff")
            y += line_height
        # save file
        image.save("images/{:03d}_1.png".format(number))
    else:
        # save file
        image.save("images/{:03d}_0.png".format(number))


def get_image_audio(filename):
    os.system(
        "ffmpeg -loop 1 -i images/{}.png -i audios/{}.mp3 -c:v libx264 -tune stillimage -c:a copy -pix_fmt yuv420p  -shortest videos/{}.mp4 -v quiet -stats -y".format(
            filename, filename, filename
        )
    )


def render_video():
    cwd = os.getcwd()
    filenames = [s[:-4] for s in os.listdir(cwd + "/images") if s.endswith(".png")]
    filenames.sort()

    print("Generating parts")
    with open("videos_paths.txt", "w") as file:
        for filename in filenames:
            print(filename)
            get_image_audio(filename)
            file.write("file videos/{}.mp4\n".format(filename))
    print("Concatenating every part")
    os.system(
        "ffmpeg -f concat -i videos_paths.txt -vf 'scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1' output.mp4 -v quiet -stats -y"
    )
    os.system("rm videos_paths.txt")


def cleanup():
    os.system("rm -rf audios")
    os.system("rm -rf images")
    os.system("rm -rf videos")


def validComment(comment):
    return (
        comment.body != "[deleted]"
        and comment.author is not None
        and "moderator" not in comment.author.name.lower()
    )


def generate_info(title, author, url):
    with open("title_description.txt", "w") as file:
        file.write("{} (r/Portugal)\n\n\n\n".format(title))
        file.write("Post - u/{}\n{}\n\n".format(author, url))
        file.write(
            'Qual o próximo post que gostariam de ver?\n\nCostumo ver este tipo de vídeos do "r/AskReddit" e decidi fazer um bot em Português. Ainda está um pouco primitivo, mas o conceito está lá.\n\nhttps://afonsoraposo.com/'
        )


def generate_thumb(title, image_url):
    width = 1920
    font_size = 64
    title_line_height = int(96 * 1.3)
    while True:
        font_width = font_size // 1.55
        line_height = int(font_size * 1.5)

        lines_title = textwrap.wrap(title, width=int(((width - 10) // 2) // font_width))
        lines_title_nr = len(lines_title) + 1
        if lines_title_nr * line_height < 1080 - title_line_height:
            font_size = int(font_size * 1.5)
        else:
            break

    response = requests.get(image_url)
    img = Image.open(BytesIO(response.content))
    img = img.resize((img.size[0] * 1080 // img.size[1], 1080))
    img = img.crop(
        (img.size[0] // 2 - 1920 // 4, 0, img.size[0] // 2 + 1920 // 4, 1080)
    )
    thumbnail = Image.new("RGBA", (1920, 1080), color="#000000")
    thumbnail.paste(img, (1920 // 2, 0))

    font = ImageFont.truetype("/usr/share/fonts/TTF/DejaVuSansMono-Bold.ttf", 96)
    font2 = ImageFont.truetype(
        "/usr/share/fonts/TTF/DejaVuSansMono-Bold.ttf", font_size
    )

    draw = ImageDraw.Draw(thumbnail)
    draw.text((20, 10), "r/Portugal", font=font, fill="#ffffff")

    y = 30 + title_line_height
    for line in lines_title:
        draw.text((20, y), line, font=font2, fill="#ffdd00")
        y += line_height

    # save file
    thumbnail.save("thumbnail.png")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(
            "Provide the thread url:\nmain.py thread-url <duration-minutes> <thumbnail-image-url>"
        )
        sys.exit()

    cleanup()

    os.makedirs("audios")
    os.makedirs("images")
    os.makedirs("videos")

    url = sys.argv[1]
    if len(sys.argv) > 2:
        duration = int(sys.argv[2]) * 60
    else:
        duration = 10 * 60

    if len(sys.argv) > 3:
        image_url = sys.argv[3]
    else:
        image_url = None

    reddit = praw.Reddit("bot1")

    submission = reddit.submission(url=url)

    title = submission.title
    description = submission.selftext.replace("\n", " ")
    author = submission.author.name

    generate_info(title, author, url)
    generate_thumb(title, image_url)

    intro_img(author, title, description, submission.score)
    duration -= read_save(title + ". " + description, "000")

    submission.comments.replace_more(limit=1)
    counter = 1
    has_comment = False
    for top_level_comment in submission.comments:
        if duration < 0:
            break
        if validComment(top_level_comment):
            comment = top_level_comment.body.replace("\n", " ")
            author = top_level_comment.author.name
            print(counter, comment)
            for second_level_comment in top_level_comment.replies:
                if validComment(second_level_comment):
                    if second_level_comment.score >= 0.5 * top_level_comment.score:
                        reply_comment = second_level_comment.body.replace("\n", " ")
                        reply_author = second_level_comment.author.name
                        has_comment = True
                        print(counter, "reply", reply_comment)
                    break
            if has_comment:
                post_img_reply(
                    author,
                    comment,
                    top_level_comment.score,
                    reply_author,
                    reply_comment,
                    second_level_comment.score,
                    counter,
                    hide=True,
                )
                post_img_reply(
                    author,
                    comment,
                    top_level_comment.score,
                    reply_author,
                    reply_comment,
                    second_level_comment.score,
                    counter,
                )
                duration -= read_save(
                    comment, "{:03d}_0".format(counter), transition=False
                )
                duration -= read_save(
                    reply_comment, "{:03d}_1".format(counter), reply=True
                )
                has_comment = False
            else:
                duration -= read_save(comment, "{:03d}_0".format(counter))
                post_img(author, comment, top_level_comment.score, counter)

            duration--
            counter += 1

    render_video()

    cleanup()

    pass
