"""LLM Client - AI Integration"""
import os, json
class LLMClient:
    def __init__(self):
        self.client = None
        self.conversation = []
        # Check env first, then config file
        api = os.environ.get('GROQ_API_KEY', '')
        if not api:
            # Try config file
            for cfg_path in ['config.json', 'bosco_os/config.json']:
                if os.path.exists(cfg_path):
                    with open(cfg_path) as f:
                        cfg = json.load(f)
                        api = cfg.get('groq_api_key', '')
                        if api: break
        if api:
            try:
                from groq import Groq
                self.client = Groq(api_key=api)
                print('[+] LLM Ready')
            except: print('[-] LLM Failed')
    
    def chat(self, msg, sys=None):
        if not self.client:
            return 'Configure GROQ_API_KEY for AI.'
        msgs = [{'role': 'system', 'content': sys or 'You are Bosco OS, helpful AI.'}]
        msgs += self.conversation[-10:]
        msgs.append({'role': 'user', 'content': msg})
        try:
            r = self.client.chat.completions.create(model='llama-3.1-8b-instant', messages=msgs, temperature=0.7, max_tokens=2048)
            resp = r.choices[0].message.content
            self.conversation.extend([{'role': 'user', 'content': msg}, {'role': 'assistant', 'content': resp}])
            return resp
        except Exception as e:
            print(f'LLM Error: {e}')
            return f'AI Error: {e}'
    
    def parse_intent(self, cmd):
        c = cmd.lower()
        if any(x in c for x in ['scan', 'nmap', 'port']): return {'intent': 'network_scan', 'target': c}
        if any(x in c for x in ['cpu', 'memory', 'disk']): return {'intent': 'system_info'}
        return {'intent': 'conversation'}

_llm = None
def get_llm(): global _llm; _llm = _llm or LLMClient(); return _llm
