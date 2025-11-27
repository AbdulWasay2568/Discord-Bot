import discord
from discord.ext import commands
from discord.ui import View, Button, Modal, TextInput
from datetime import datetime
from bot.utils.db_handler import filter_command
import os

class InputModal(Modal):
    def __init__(self, title: str, label: str, callback):
        super().__init__(title=title)
        self.input_field = TextInput(label=label, required=True)
        self.add_item(self.input_field)
        self.callback = callback  # function to call on submit

    async def on_submit(self, interaction: discord.Interaction):
        try:
            # Call the callback (update filters in the parent view)
            await self.callback(interaction, self.input_field.value)

            # Acknowledge silently (no message shown)
            await interaction.response.defer()
        except Exception as e:
            print("Modal submit error:", e)

class FiltersView(View):
    def __init__(self):
        super().__init__(timeout=300)

        # Initialize filter data
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

        # Dynamic button config: (label, key)
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

        # Add input buttons dynamically
        for label,input_label,key in button_configs:
            self.add_item(self.create_input_button(label, input_label, key))

        # Add Submit button with proper callback
        submit_button = Button(label="Submit", style=discord.ButtonStyle.green, custom_id="submit")
        submit_button.callback = self.submit_callback
        self.add_item(submit_button)

    # Create button with dynamic callback
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

    # Handle input from modals
    async def handle_input(self, interaction, value, key):
        if key in ["channels", "members", "reactions"]:
            # Parse comma-separated values and strip whitespace
            parsed_values = [v.strip() for v in value.split(",") if v.strip()]
            self.filters[key] = parsed_values
            print(f"DEBUG list.py: Set {key} = {parsed_values}")
        elif key in ["from_date", "to_date"]:
            try:
                self.filters[key] = datetime.fromisoformat(value)
                print(f"DEBUG list.py: Set {key} = {self.filters[key]}")
            except ValueError:
                await interaction.response.send_message(
                    f"Invalid date format for {key}. Use YYYY-MM-DD",
                    ephemeral=True
                )
        elif key == "has_attachments":
            # Parse boolean
            bool_value = value.lower() in ["true", "yes", "1", "on"]
            self.filters[key] = bool_value
            print(f"DEBUG list.py: Set {key} = {bool_value}")
        elif key == "limit":
            try:
                self.filters[key] = int(value)
                print(f"DEBUG list.py: Set {key} = {self.filters[key]}")
            except ValueError:
                self.filters[key] = 20
                print(f"DEBUG list.py: Invalid limit, set to default 20")
        else:
            self.filters[key] = value
            print(f"DEBUG list.py: Set {key} = {value}")

    # Callback for Submit button
    async def submit_callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        try:
            # Execute the filter command to get matching messages
            messages = await filter_command(self.filters)
            
            if messages:
                print(f"DEBUG: Messages count: {len(messages)}")
            
            if not messages:
                await interaction.followup.send(
                    "No messages found matching the selected filters.",
                    ephemeral=True
                )
                return
            
            output_dir = "filtered_messages"
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = os.path.join(output_dir, f"messages_{timestamp}.txt")
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("=" * 80 + "\n")
                f.write("MESSAGE SEARCH RESULTS\n")
                f.write("=" * 80 + "\n\n")
                
                f.write("FILTERS APPLIED:\n")
                f.write("-" * 80 + "\n")
                f.write(f"Channels: {', '.join(self.filters['channels']) if self.filters['channels'] else 'All channels'}\n")
                f.write(f"Members: {', '.join(self.filters['members']) if self.filters['members'] else 'All members'}\n")
                f.write(f"Reactions: {', '.join(self.filters['reactions']) if self.filters['reactions'] else 'All reactions'}\n")
                f.write(f"From Date: {self.filters['from_date'].strftime('%Y-%m-%d') if self.filters['from_date'] else 'Not set'}\n")
                f.write(f"To Date: {self.filters['to_date'].strftime('%Y-%m-%d') if self.filters['to_date'] else 'Not set'}\n")
                f.write(f"Has Attachments: {self.filters['has_attachments']}\n")
                f.write(f"Sort By: {self.filters['sort_by']}\n")
                f.write(f"Total Results: {len(messages)} messages\n")
                f.write("\n" + "=" * 80 + "\n\n")
                
                # Write each message
                for i, msg in enumerate(messages, 1):
                    try:
                        f.write(f"MESSAGE {i}\n")
                        f.write("-" * 80 + "\n")
                        f.write(f"Message ID: {msg.id}\n")
                        f.write(f"Channel ID: {msg.channel_id}\n")
                        f.write(f"Author ID: {msg.author_id}\n")
                        f.write(f"Timestamp: {msg.timestamp}\n")
                        
                        if msg.edited_timestamp:
                            f.write(f"Edited Timestamp: {msg.edited_timestamp}\n")
                        
                        f.write(f"\nContent:\n")
                        f.write(f"{msg.content if msg.content else '(No content)'}\n")
                        
                        if msg.attachments and len(msg.attachments) > 0:
                            f.write(f"\nAttachments ({len(msg.attachments)}):\n")
                            for att in msg.attachments:
                                f.write(f"  - {att.get('filename', 'Unknown')} ({att.get('size', '?')} bytes)\n")
                                f.write(f"    URL: {att.get('url', 'N/A')}\n")
                                f.write(f"    Local Path: {att.get('local_path', 'Not downloaded')}\n")
                        
                        if msg.reactions and len(msg.reactions) > 0:
                            f.write(f"\nReactions ({len(msg.reactions)}):\n")
                            for reaction in msg.reactions:
                                emoji_name = reaction.get('emoji', {}).get('name', 'Unknown')
                                count = reaction.get('count', 0)
                                f.write(f"  - {emoji_name} x{count}\n")
                        
                        if msg.embeds and len(msg.embeds) > 0:
                            f.write(f"\nEmbeds ({len(msg.embeds)}):\n")
                            for embed in msg.embeds:
                                f.write(f"  - Title: {embed.get('title', 'No title')}\n")
                                f.write(f"    Description: {embed.get('description', 'No description')}\n")
                        
                        f.write("\n\n")
                        
                    except Exception as msg_err:
                        print(f"DEBUG: Error processing message {i}: {msg_err}")
                        f.write(f"ERROR: Failed to process this message: {msg_err}\n\n")
                        continue
            
            embed = discord.Embed(
                title="Messages Exported",
                description=f"Successfully exported {len(messages)} messages to a text file.",
                color=discord.Color.green()
            )
            embed.add_field(name="Filename", value=output_file, inline=False)
            embed.add_field(name="Messages Found", value=str(len(messages)), inline=True)
            
            with open(output_file, 'rb') as f:
                await interaction.followup.send(
                    embed=embed,
                    file=discord.File(f, filename=os.path.basename(output_file)),
                    ephemeral=True
                )
                
        except Exception as e:
            print(f"Error in submit_callback: {e}")

@commands.command()
async def list(ctx):
    view = FiltersView()
    embed = discord.Embed(
        title="Select Filters",
        description="Use the buttons below to set filters, then click Submit to see the selected filters.",
        color=discord.Color.blue()
    )
    await ctx.send(embed=embed, view=view, ephemeral=True)
