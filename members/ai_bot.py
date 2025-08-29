import os
import threading
from typing import List, Optional

# Lazy state
_model_lock = threading.Lock()
_model = None
_default_gen_model = os.environ.get('AI_TEXT_GEN_MODEL', 'distilgpt2')


def _load_pipeline_optional():
	"""Try to load a local transformers pipeline if libs are installed; otherwise None."""
	global _model
	with _model_lock:
		if _model is not None:
			return _model
		try:
			from transformers import pipeline  # type: ignore
			_model = pipeline('text-generation', model=_default_gen_model, device=-1)
			return _model
		except Exception:
			_model = None
			return None


def _hf_generate(prompt: str) -> Optional[str]:
	"""Call Hugging Face Inference API if HF_API_TOKEN is set. Returns text or None."""
	hf_token = os.environ.get('HF_API_TOKEN') or os.environ.get('HUGGINGFACEHUB_API_TOKEN')
	if not hf_token:
		return None
	model_id = os.environ.get('HF_MODEL_ID', 'google/gemma-2-2b-it')
	api_url = f"https://api-inference.huggingface.co/models/{model_id}"
	payload = {
		"inputs": prompt,
		"parameters": {"max_new_tokens": 120, "temperature": 0.7, "top_p": 0.9},
	}
	try:
		import requests  # type: ignore
		headers = {"Authorization": f"Bearer {hf_token}", "Accept": "application/json"}
		resp = requests.post(api_url, headers=headers, json=payload, timeout=30)
		resp.raise_for_status()
		data = resp.json()
		if isinstance(data, list) and data and isinstance(data[0], dict):
			gen = data[0].get('generated_text')
			if isinstance(gen, str) and gen:
				return gen[len(prompt):].strip() or gen.strip()
			for key in ('summary_text', 'text'):
				if key in data[0] and isinstance(data[0][key], str):
					return data[0][key].strip()
		elif isinstance(data, dict):
			for key in ('generated_text', 'summary_text', 'text'):
				val = data.get(key)
				if isinstance(val, str) and val:
					return val.strip()
		return None
	except Exception:
		return None


def _intent_reply(prompt: str) -> Optional[str]:
	"""Deterministic, domain-aware replies for common intents like login/register/browse/open dashboard."""
	p = (prompt or '').strip().lower()
	if not p:
		return None

	def _has(*words: str) -> bool:
		return all(w in p for w in words)

	# Role detection
	role = None
	if 'shopkeeper' in p:
		role = 'shopkeeper'
	elif 'delivery' in p:
		role = 'delivery'
	elif 'customer' in p:
		role = 'customer'

	# Login
	if any(w in p for w in ['login', 'log in', 'sign in']):
		if role == 'shopkeeper':
			return "To login as Shopkeeper, click the Shopkeeper button, then Login. I can also start a step-by-step login here: say 'shopkeeper login'."
		if role == 'delivery':
			return "To login as Delivery Partner, click the Delivery button, then Login. I can also start step-by-step login: say 'delivery login'."
		if role == 'customer':
			return "To login as Customer, click the Customer button, then Login. I can also start step-by-step login: say 'customer login'."
		return "Who would you like to login as: Shopkeeper, Customer, or Delivery? You can say 'shopkeeper login', 'customer login', or 'delivery login'."

	# Register
	if any(w in p for w in ['register', 'sign up', 'create account']):
		if role == 'shopkeeper':
			return "To register a Shop, click Shopkeeper → Register. I can also create your account step-by-step: say 'shopkeeper register'."
		if role == 'delivery':
			return "To register as Delivery Partner, click Delivery → Register. I can also create your account step-by-step: say 'delivery register'."
		if role == 'customer':
			return "To register as Customer, click Customer → Register. I can also create your account step-by-step: say 'customer register'."
		return "Who would you like to register as: Shopkeeper, Customer, or Delivery? Say 'shopkeeper register', 'customer register', or 'delivery register'."

	# Open dashboard
	if any(w in p for w in ['dashboard', 'open dashboard', 'my dashboard']):
		if role == 'shopkeeper':
			return "Opening the Shopkeeper dashboard. If it doesn't open automatically, click Shopkeeper → Dashboard. You can also say 'view products' or 'view orders'."
		if role == 'delivery':
			return "Opening the Delivery dashboard. If it doesn't open automatically, click Delivery → Dashboard."
		if role == 'customer':
			return "Opening the Customer dashboard. If it doesn't open automatically, click Customer → Browse Products."
		return "Which dashboard should I open: Shopkeeper, Customer, or Delivery?"

	# Browse products (customer-side discovery)
	if any(_has(w) for w in [('browse', 'products'), ('show', 'products'), ('find', 'products')]) or 'browse products' in p or 'products' in p:
		return "You can browse products from the Customer menu or by saying 'customer dashboard'. I can also list product names — try 'search rice' or 'search oil'."

	# Orders intents
	if 'orders' in p or _has('view', 'orders'):
		if role == 'shopkeeper':
			return "Opening shopkeeper orders. If you are on the dashboard, the bot can open the Orders modal automatically — say 'view orders'."
		if role == 'customer':
			return "You can view your orders at Customer → Orders. Say 'customer orders' to navigate."
		if role == 'delivery':
			return "Go to Delivery → Dashboard to see available/assigned orders."
		return "Do you want Shopkeeper orders or Customer orders?"

	# Fallback for other help requests
	if any(w in p for w in ['help', 'assist', 'support']):
		return "I can help you login/register, open dashboards, browse products, and view orders. Tell me your role (Shopkeeper/Customer/Delivery) and what you want to do."

	return None


def generate_ai_reply(messages: List[dict]) -> str:
	"""Generate a reply given a chat history. Prefers local pipeline; falls back to HF API; then rules.
	Also includes deterministic intent handling so common UX requests are always answered well."""
	user_texts = [m['content'] for m in messages if m.get('role') == 'user']
	prompt = user_texts[-1] if user_texts else ''

	# 0) Intent handler first – ensures consistent UX answers
	intent_text = _intent_reply(prompt)
	if intent_text:
		return intent_text

	# 1) Try local transformers pipeline if available
	pipe = _load_pipeline_optional()
	if pipe is not None and prompt:
		try:
			out = pipe(prompt, max_new_tokens=100, do_sample=True, top_p=0.9, temperature=0.7, num_return_sequences=1)
			text = out[0].get('generated_text', '') if isinstance(out, list) else ''
			return (text[len(prompt):].strip() or text.strip() or _rule_fallback(prompt))
		except Exception:
			pass

	# 2) Try hosted Hugging Face Inference API if token present
	if prompt:
		gen = _hf_generate(prompt)
		if gen:
			return gen

	# 3) Rule-based fallback
	return _rule_fallback(prompt)


def _rule_fallback(prompt: str) -> str:
	if not prompt:
		return "Hi! Ask me anything about products, orders, payments, and delivery."
	lower = prompt.lower()
	if any(k in lower for k in ['order','track','delivery','shipping']):
		return "You can track orders from your dashboard > Orders. Need help with a specific order?"
	if any(k in lower for k in ['pay','payment','card','upi','wallet']):
		return "We support cards, UPI, wallets and COD. Online payments are secure."
	if any(k in lower for k in ['return','refund','exchange']):
		return "Most items have a 7–14 day return window. Open your order and choose Return."
	return f"You asked: '{prompt}'. I can help with shopping, orders, payments and delivery."
