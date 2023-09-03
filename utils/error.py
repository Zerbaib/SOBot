import disnake

from utils import var



def error_embed(e):
    """
    Create an embed with an error message.

    Parameters:
        title (str): The title of the error embed.
        description (str): The description of the error embed.

    Returns:
        disnake.Embed: The error embed.
    """
    issue_link = var.issues_link
    embed = disnake.Embed(
        title=f"A error as poped !",
        description=f"The exception is\n\n```{e}```",
        color=disnake.Color.red()
    )
    embed.add_field(
        name="You can now create a Issue on GitHub",
        value=f"Tell us what command and the exeption [**here**]({issue_link})"
    )
    return embed