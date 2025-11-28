import discord
from discord.ext import commands
from discord.ui import View, Button, Modal, TextInput
from datetime import datetime
from bot.utils.db_handler import filter_command
import io

class InputModal(Modal):
    def __init__(self, title: str, label: str, callback):
        super().__init__(title=title)
        self.input_field = TextInput(label=label, required=True)
        self.add_item(self.input_field)
        self.callback = callback  

    async def on_submit(self, interaction: discord.Interaction):
        try:
            await self.callback(interaction, self.input_field.value)

            await interaction.response.defer()
        except Exception as e:
            print("Modal submit error:", e)

class FiltersView(View):
    def __init__(self):
        super().__init__(timeout=300)

        self.filters = {
            "channels": [],
            "members": [],
            "reactions": [],
            "from_date": None,
            "to_date": None,
            "has_attachments": False,
            "attachment_name_contains": "",
            "sort_by": "created_descending",
            "limit":20
        }

        button_configs = [
            ("Set Channel(s)","Enter channel(s) separated by commas", "channels"),
            ("Set Member(s)","Enter member(s) separated by commas", "members"),
            ("Set From Date","Enter from date [YYYY-MM-DD]", "from_date"),
            ("Set To Date","Enter to date [YYYY-MM-DD]", "to_date"),
            ("Set Reaction(s)","Enter reaction(s) separated by commas", "reactions"),
            ("Has Attachments","Has attachments? [True/False]", "has_attachments"),
            ("Attachment Name Contains","Enter attachment name contains", "attachment_name_contains"),
            ("Sort By","Sort by [asc/desc/reactions_desc]", "sort_by"),
            ("Limit","Enter limit [number]", "limit"),
        ]

        for label,input_label,key in button_configs:
            self.add_item(self.create_input_button(label, input_label, key))

        submit_button = Button(label="Submit", style=discord.ButtonStyle.green, custom_id="submit")
        submit_button.callback = self.submit_callback
        self.add_item(submit_button)

    def create_input_button(self, label, input_label, key):
        button = Button(label=label, style=discord.ButtonStyle.primary, custom_id=key)

        async def button_callback(interaction: discord.Interaction):
            await interaction.response.send_modal(
                InputModal(
                    title=label,
                    label=input_label,
                    callback=lambda i, v: self.handle_input(i, v, key)
                )
            )

        button.callback = button_callback
        return button

    async def handle_input(self, interaction, value, key):
        if key in ["channels", "members", "reactions"]:
            parsed_values = [v.strip() for v in value.split(",") if v.strip()]
            self.filters[key] = parsed_values
        elif key in ["from_date", "to_date"]:
            try:
                self.filters[key] = datetime.fromisoformat(value)
            except ValueError:
                await interaction.response.send_message(
                    f"Invalid date format for {key}. Use YYYY-MM-DD",
                    ephemeral=True
                )
        elif key == "has_attachments":
            bool_value = value.lower() in ["true", "yes", "1", "on"]
            self.filters[key] = bool_value
        elif key == "limit":
            try:
                self.filters[key] = int(value)
            except ValueError:
                self.filters[key] = 20
        else:
            self.filters[key] = value

    async def submit_callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        try:
            messages = await filter_command(self.filters)            
            if messages:
                print(f"Messages count: {len(messages)}")
            
            if not messages:
                await interaction.followup.send(
                    "No messages found matching the selected filters.",
                    ephemeral=True
                )
                return
            
            output_text = "FILTERS APPLIED:\n\n"
            output_text += f"Channels: {', '.join(self.filters['channels']) if self.filters['channels'] else 'All channels'}\n"
            output_text += f"Members: {', '.join(self.filters['members']) if self.filters['members'] else 'All members'}\n"
            output_text += f"Reactions: {', '.join(self.filters['reactions']) if self.filters['reactions'] else 'All reactions'}\n"
            output_text += f"From Date: {self.filters['from_date'].strftime('%Y-%m-%d') if self.filters['from_date'] else 'Not set'}\n"
            output_text += f"To Date: {self.filters['to_date'].strftime('%Y-%m-%d') if self.filters['to_date'] else 'Not set'}\n"
            output_text += f"Has Attachments: {self.filters['has_attachments']}\n"
            output_text += f"Sort By: {self.filters['sort_by']}\n"
            output_text += f"Total Results: {len(messages)} messages\n"
            output_text += "\n" + "=" * 80 + "\n\n"
            
            for i, msg in enumerate(messages, 1):
                try:
                    output_text += f"MESSAGE {i}\n"
                    output_text += "-" * 80 + "\n"
                    output_text += f"Message ID: {msg.id}\n"
                    output_text += f"Channel ID: {msg.channel_id}\n"
                    output_text += f"Author ID: {msg.author_id}\n"
                    output_text += f"Timestamp: {msg.timestamp}\n"
                    
                    if msg.edited_timestamp:
                        output_text += f"Edited Timestamp: {msg.edited_timestamp}\n"
                    
                    output_text += f"\nContent:\n"
                    output_text += f"{msg.content if msg.content else '(No content)'}\n"
                    
                    if msg.attachments and len(msg.attachments) > 0:
                        output_text += f"\nAttachments ({len(msg.attachments)}):\n"
                        for att in msg.attachments:
                            output_text += f"  - {att.get('filename', 'Unknown')} ({att.get('size', '?')} bytes)\n"
                            output_text += f"    URL: {att.get('url', 'N/A')}\n"
                            output_text += f"    Local Path: {att.get('local_path', 'Not downloaded')}\n"
                    
                    if msg.reactions and len(msg.reactions) > 0:
                        output_text += f"\nReactions ({len(msg.reactions)}):\n"
                        for reaction in msg.reactions:
                            emoji_name = reaction.get('emoji', {}).get('name', 'Unknown')
                            count = reaction.get('count', 0)
                            output_text += f"  - {emoji_name} x{count}\n"
                    
                    if msg.embeds and len(msg.embeds) > 0:
                        output_text += f"\nEmbeds ({len(msg.embeds)}):\n"
                        for embed in msg.embeds:
                            output_text += f"  - Title: {embed.get('title', 'No title')}\n"
                            output_text += f"    Description: {embed.get('description', 'No description')}\n"
                    
                    output_text += "\n\n"
                    
                except Exception as msg_err:
                    print(f"Error processing message ID {msg.id}: {msg_err}")
                    continue
            
            embed = discord.Embed(
                title="Messages Found",
                description=f"Successfully found {len(messages)} messages matching your filters.",
                color=discord.Color.green()
            )
            embed.add_field(name="Total Results", value=str(len(messages)), inline=True)
            embed.add_field(name="Sort Order", value=self.filters['sort_by'], inline=True)
            
            file = discord.File(
                io.BytesIO(output_text.encode('utf-8')),
                filename=f"messages_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            )
            await interaction.followup.send(embed=embed, file=file, ephemeral=True)
                
        except Exception as e:
            print(f"Error in submit_callback: {e}")
            await interaction.followup.send(f"Error processing filters: {str(e)}", ephemeral=True)

@commands.command()
async def list(ctx):
    view = FiltersView()
    embed = discord.Embed(
        title="Select Filters",
        description="Use the buttons below to set filters, then click Submit to see the selected filters.",
        color=discord.Color.blue()
    )
    await ctx.send(embed=embed, view=view, ephemeral=True)
