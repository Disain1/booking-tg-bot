from PIL import Image, ImageDraw, ImageFont

def getTicketImage(row: int, place: int):
    ticket = Image.open('images/ticket/ticket.jpg')
    draw_text = ImageDraw.Draw(ticket)

    font = ImageFont.truetype("images/ticket/Roboto-Medium.ttf", size=36)
    draw_text.text((370, 1073), f"{place}", fill="#FFFFFF", font=font)
    draw_text.text((320, 1115), f"{row}", fill="#FFFFFF", font=font)

    path = f"tickets/ticket{row}{place}.png"
    ticket.save(path)
    return open(path, "rb")