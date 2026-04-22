using AluguelCarros.Models;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;

namespace AluguelCarros.Controllers
{
    public class ClienteController : Controller
    {
        private readonly AppDbContext _context;

        public ClienteController(AppDbContext context)
        {
            _context = context;
        }

        // Lista todos os clientes
        public async Task<IActionResult> Index()
        {
            var clientes = await _context.Clientes.ToListAsync();
            return View(clientes);
        }

        // Exibe formulário de cadastro
        public IActionResult Criar()
        {
            return View();
        }

        // Salva o novo cliente no banco
        [HttpPost]
        public async Task<IActionResult> Criar(Cliente cliente)
        {
            if (ModelState.IsValid)
            {
                _context.Clientes.Add(cliente);
                await _context.SaveChangesAsync();
                return RedirectToAction(nameof(Index));
            }
            return View(cliente);
        }

        // Exibe formulário de edição
        public async Task<IActionResult> Editar(int id)
        {
            var cliente = await _context.Clientes.FindAsync(id);
            if (cliente == null) return NotFound();
            return View(cliente);
        }

        // Salva as alterações do cliente
        [HttpPost]
        public async Task<IActionResult> Editar(Cliente cliente)
        {
            if (ModelState.IsValid)
            {
                _context.Clientes.Update(cliente);
                await _context.SaveChangesAsync();
                return RedirectToAction(nameof(Index));
            }
            return View(cliente);
        }

        // Exclui o cliente
        public async Task<IActionResult> Excluir(int id)
        {
            var cliente = await _context.Clientes.FindAsync(id);
            if (cliente == null) return NotFound();
            _context.Clientes.Remove(cliente);
            await _context.SaveChangesAsync();
            return RedirectToAction(nameof(Index));
        }
    }
}