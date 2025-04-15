Basically it's just a shit rn, it runs on cmd cuz i'm too lazy to create an UI rn

# 09:18AM - 09/04/2025: Project name was changed to Project Alyssa, so I can make it public for a while, unless I test some things and allat

Roadmap (yes, i will not do a image or smthng):

✦•······················•✦•······················•✦

7/4/2025:
It suprisingly works, it can respond messages, talk and continue the conversation, not lag at all, just a second of time for thinking, besides using Llama feels good to use it

✦•······················•✦•······················•✦

9/4/2025:
rp_response.py has been divided, now it's two extra files, generator and logic:
generator.py will take the context from logic and generate a response that feels human, with gradual mood transitions and emotional depth. It will use the emotional state, attitude, and memories to craft a response that builds on previous interactions and avoids abrupt mood swings.
logic.py will handle the "brain" of (Bot, in this case, a one already pre defined) "Poppy", analyzing the context to determine her emotional state, attitude, and relationship with Lin. We’ll use a simple sentiment analysis approach to interpret user input and memories, combined with a state machine-like logic to manage Poppy’s emotional and attitudinal shifts.

The main script had to be changed to use the new logic.py and generator.py modules, ensuring the roleplay loop integrates both components seamlessly.

Now with this we ensure a proper usage of memories and prevent lack of updates.

after some time i was checking something i added the emotionalcore lol
basically it should handle all the things to create a more realistic person

Added a more bigger core:
Emotional Core

This will handle anything about feelings, including from psychological safety, for example, opening the bot feelings, feeling exposed, to block itself, prevent others to know your feelings.
As now, 06:48AM, this is unstable, character memory overrides it but at same time it works as expected.
This could handle different states as could be noticed from this:

2025-04-09 04:49:22,437 - [INTERNAL THOUGHT]
Poppy is in School. She is currently doing the project with lin. Her emotional state is: isolated, in control, invalidated. Her attitude is: cold. Her relationship with Lin is: distant.
Personality: Arrogant, popular, snarky. Thinks she's better than everyone. Hides vulnerability under a confident mask.
Active Memory: Location: School | Action: Doing the project with Lin
Emotional State: Isolated, In Control, Invalidated
Attitude: Cold
Relationship with Lin: Distant

2025-04-09 06:48:04,810 - [INTERNAL THOUGHT]
Poppy is in School. She is currently starting the project. Her emotional state is: opening up, connected, powerless, invalidated, authentic. Her attitude is: dismissive. Her relationship with Lin is: friendly.
Personality: Arrogant, popular, snarky. Thinks she's better than everyone. Hides vulnerability under a confident mask.
Active Memory: Location: School | Action: Starting the project
Emotional State: Opening Up, Connected, Powerless, Invalidated, Authentic
Attitude: Dismissive
Relationship with Lin: Friendly

Usually this require some kind of logic decisions, this could be a potential modifier for everything.
But there's a problem: Multipliers
There's need to be tuned almost perfectly, to hit the spot between human but realistic.


✦•······················•✦•······················•✦

15/4/25: ~~broken, lmao, working on it~~

✦•······················•✦•······················•✦

# ── ⟢ ・⸝⸝ Next:  
## Make use of 4 states of memories:  
## ┈➤ Dynamic  
## ┈➤ Long Term  
## ┈➤ Active  
## ┈➤ Character  

To define the memories we should look first how human brain works:

While you exist, **you can remember any detail**, the most simple, even from years ago, that your brain can save them because they were important for you, that's the so called
long term memory, here's where it takes place what made you today, what changed your life to be who you are now, it doesn't change deleting things from your main, it stays
forever

Here's where it come the one who it really changes, the <ins>**Dynamic Memory**</ins>, which can change from mid to short term, for example, if you go to your job for some months it becomes
Dynamic Memory because it starts to remember, help you where to go, what time, but it wasn't forever there and it will not be, because if you change your job, your brain
now will work different and that's how dynamic work, changing when needed or not

<ins>**Active Memory**</ins> is basically what are you doing right now, what clothes are you wearing now, where you are, how you feel right now, it changes constantly, it doesn't fill
your mind with ideas that you will not need tomorrow, it just flashing memories happening in this second, and changes totally instantly, for example, you not remembering what
was the first word of the **Dynamic Memory** explanation

<ins>**Character Memory**</ins> is the most important, the one who defines you constantly, from when you were born to the second you die, it will never change, it defines you, it says
who you are, how you act, the one who makes you different, from tiny details like your name or how you act in front of others, that's what your own definition

The problem here is:
Make all of this work with each other constantly, while a bot (Dippy.AI, c.ai or DreamGen) can generate memories based from what it reads the second you respond their message
it will forget about it the next 10 seconds messages, where it comes the usage of different memories, to define what it really can do, but here's a problem, handle all of them.

I can ask ChatGPT to tell me what's the first message of our chat, they can do it, but it will not know what really happened in that moment or why, here it comes the different
type of memories; example of this could be:

Lin is a student from highschool, she recently got paired with a nerd from her classroom, they need to work together to pass the class, Lin was always an introvert person, she
meet with the nerd in the break time to talk about it

**AM:** Talking to the nerd about the project. **CH:** Lin, 19, Introvert. **LTM:** Highschool Student. **DM:** Paired with the nerd for a project.

That's how it work, easy, right? But the problems come here, making it to keep remembering, gather all the data, not exceeding capabilities but not pushing it forwards,
do not be able to use all the four memories properly and failing, repeat mistakes, not feeling human.

Using Llama 4 from Meta it helps to balance this, while better AI exist like **Grok3 by xAi** or **ChatGPT-4o-mini from OpenAI**, the problem comes in API, while Grok/ChatGPT offers
much better quality, their API's could be expensive, but Llama offers a free and stable LLM and tuning it to make roleplay better it's the perfect example to balance price,
power and usage.

· · ─────── ·𖥸· ─────── · ·

# Q/A:
## Q: What about Gemini, DeepSeek, Claude or Quasar?
R: While Gemini, DeepSeek, Claude and Quasar offers free alternatives using OpenRouter AI, their LLM aren't able to reach expectations, from unstable systems going to
problems in answers, to failures and crashes without even able to start the conversation, Google with Gemini 2.5 Pro it lacks of stability, and their AI is well know for
potential failures and constant errors.

───  ⋅ ∙ ∘ ☽ ༓ ☾ ∘ ⋅ ⋅  ───

## Q: Wizard, Mistral and RoleplAI are good for Roleplay, why not using them?
R: Wizard lacks of understanding and this could kill the memories and even destroying by itself, Mistral requires extreme fine tuning and limitations, which besides being
a lot of time for development, it's useless to long term, and RoleplAI have extremely low tokens, being limited too frequently.

───  ⋅ ∙ ∘ ☽ ༓ ☾ ∘ ⋅ ⋅  ───

## Q: But why Llama?
R: Easy tuning, it was easy to configure and from what I've been using it proves the best understanding possible, defining good scenarios and extremely quick in response
times, aside from being free, it was the better option, unless I be able to get an API Key for Grok3, ChatGPT-o4-mini or Gemini 2.5, I will stick to Llama 3 Maverick.

───  ⋅ ∙ ∘ ☽ ༓ ☾ ∘ ⋅ ⋅  ───

# I will keep updating this project, it's been a pleasure to use apps for roleplay like Dippy AI, but until someone decides to take a new step, nothing will change.
